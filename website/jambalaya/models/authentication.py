from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from django.core.exceptions import MultipleObjectsReturned

from models import User


def get_one_translating_exceptions(query):
    """
    Return a single result from the given query. Translate sqlalchemy exceptions to the Django equivalents.
    """
    try:
        return query.one()
    except NoResultFound:
        raise ShimUser.DoesNotExist
    except MultipleResultsFound:
        raise MultipleObjectsReturned


class ShimUserManager(UserManager):
    """
    Django model manager for ShimUser. Mostly in place for implementing get().
    """
    # Translates Django model field names to sqlalchemy model field names, and vice-versa
    FIELD_MAP = None
    FIELDS = None
    IGNORED_FIELDS = ["groups", "is_active", "user_permissions", "is_superuser"]

    @classmethod
    def create_translation_map(cls):
        """
        Builds a bidirectional map of Django <=> sqlalchemy field names for the User model.
        Django field names are formatted like this: first_name
        whereas our sqlalchemy fields look like this: FirstName
        """
        if cls.FIELD_MAP is not None:
            return

        cls.FIELD_MAP = {}
        cls.FIELDS = [field for field in ShimUser._meta.get_all_field_names() if field not in cls.IGNORED_FIELDS]
        for django_field in cls.FIELDS:
            if django_field == "id":
                sqlalchemy_field = "ID"
            else:
                sqlalchemy_field = "".join([a.title() for a in django_field.split("_")])
            cls.FIELD_MAP[django_field] = sqlalchemy_field
            cls.FIELD_MAP[sqlalchemy_field] = django_field

    def create_user(self, username, email=None, password=None, **kwargs):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = ShimUser(username=username, email=email, date_joined=now, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **kwargs):
        raise NotImplementedError()

    def get(self, **kwargs):
        """
        Get a single ShimUser (or throw an exception) matching the given criteria
        """
        from jambalaya.settings import Session

        self.create_translation_map()
        if "pk" in kwargs:
            # pk means primary key - replace by id (our actual primary key)
            kwargs["id"] = kwargs["pk"]
            del kwargs["pk"]
        new_kwargs = {self.FIELD_MAP[k]: kwargs[k] for k in kwargs}
        session = Session()
        query = session.query(User).filter_by(**new_kwargs)
        user = get_one_translating_exceptions(query)
        ret = ShimUser.from_sqlalchemy_user(user)
        session.close()
        return ret


class ShimUser(AbstractUser):
    """
    A fake Django ORM model object for the authentication system to use. This class redirects attempts to create or
    modify users to the appropriate sqlalchemy methods. It is designed to be invisible to the rest of the system.

    WARNING: You cannot access related objects (e.g. the user's reviews or addresses) directly through this class.
             To do that you need to work with the sqlalchemy model instance.
    """
    objects = ShimUserManager()

    class Meta:
        managed = False

    @staticmethod
    def from_sqlalchemy_user(user):
        kwargs = {field: getattr(user, ShimUserManager.FIELD_MAP[field]) for field in ShimUserManager.FIELDS}
        return ShimUser(**kwargs)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        from jambalaya.settings import Session

        ShimUserManager.create_translation_map()
        if force_insert and (force_update or update_fields):
            raise ValueError("Cannot force both insert and updating in model saving.")

        session = Session()

        if self.id:
            query = session.query(User).filter(User.ID == self.id)
            user = get_one_translating_exceptions(query)
        else:
            user = User()
            update_fields = ShimUserManager.FIELDS

        for django_field in update_fields:
            sqlalchemy_field = ShimUserManager.FIELD_MAP[django_field]
            v = getattr(self, django_field)
            if sqlalchemy_field in ["DateJoined", "LastLogin"]:
                # SQLAlchemy doesn't want timezone information in its timestamps
                v = v.astimezone(timezone.utc).replace(tzinfo=None)
            setattr(user, sqlalchemy_field, v)

        if not self.id:
            session.add(user)

        session.commit()

    def delete(self, using=None):
        from jambalaya.settings import Session

        if self.id:
            session = Session()
            session.filter(User.ID == self.id).delete()
            session.commit()

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False