import dateutil.parser
import datetime

from django.utils.functional import SimpleLazyObject
from django.core.urlresolvers import resolve
from django.contrib.auth import logout
from django.contrib import messages

from jambalaya.models import User
from jambalaya import settings


class UsernameLookupMiddleware(object):
    """
    Allows users to login with either their email or username. The Django auth module only supports username login.
    This middleware sits in between the login request and the auth module. When it sees an email address, it looks up
    the associated username and modifies the request.
    """

    def process_request(self, request):
        match = resolve(request.path)
        if not match or match.url_name != "login":
            return

        if (request.method == "POST") and ("username" in request.POST):
            # request.POST is immutable, so copy it then modify it
            request.POST = request.POST.copy()
            username = request.POST["username"]
            if "@" in username:
                session = request.db_session
                username = session.query(User.Username).filter(User.Email == username).scalar()
                request.POST["username"] = username


class SQLAlchemyUserProviderMiddleware(object):
    def process_request(self, request):
        if not hasattr(request, "s_user") and hasattr(request, "user") and request.user.is_authenticated():
            def lazy_user_provider():
                session = request.db_session
                return session.query(User).filter(User.ID == request.user.id).one()

            request.s_user = SimpleLazyObject(lambda: lazy_user_provider())


def sqlalchemy_user_context_provider(request):
    if hasattr(request, "s_user"):
        return {
            "s_user": request.s_user
        }
    return {}


class SessionIdleTimeoutMiddleware(object):
    """
    Middleware class to timeout a session after a specified time period.
    Modified from https://github.com/subhranath/django-session-idle-timeout/blob/master/sessions/middleware.py
    """

    def process_request(self, request):
        # Timeout is done only for authenticated logged in users.
        if request.user.is_authenticated():
            current_datetime = datetime.datetime.now()

            # Timeout if idle time period is exceeded.
            if "last_activity" in request.session and (current_datetime - dateutil.parser.parse(
                    request.session['last_activity'])).seconds > settings.SESSION_IDLE_TIMEOUT:
                logout(request)
                messages.add_message(request, messages.ERROR, 'Your session has been timed out.')
            # Set last activity time in current session.
            else:
                request.session['last_activity'] = current_datetime.isoformat()
        return None