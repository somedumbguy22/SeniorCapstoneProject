"""
Django settings for jambalaya project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import logging

import django
import sqlalchemy
import sqlalchemy.orm
from django.conf import global_settings

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

USE_REMOTE_DB = False

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(t^xkuly7d$2h3+m95=(g26)qf#=w4#d^%o(yllcbz)x+je-jo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ["localhost"]

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jambalaya',
    "crispy_forms"
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'jambalaya.middleware.database.SQLAlchemySessionMiddleware',
    'jambalaya.middleware.auth.SQLAlchemyUserProviderMiddleware',
    'jambalaya.middleware.auth.UsernameLookupMiddleware',
    'jambalaya.middleware.auth.SessionIdleTimeoutMiddleware'
)

ROOT_URLCONF = 'jambalaya.urls'

WSGI_APPLICATION = 'jambalaya.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

if USE_REMOTE_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'Jambalaya',
            'USER': 'jambalaya',
            'PASSWORD': 'vecjRj_5OPzU1RzacsURv9JoZ',
            'HOST': '71.225.72.100'
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'Jambalaya',
            'USER': 'root',
            'PASSWORD': 'vecjRj_5OPzU1RzacsURv9JoZ',
            'HOST': '127.0.0.1'
        }

    }

DB = DATABASES["default"]
engine_string = "mysql://%s:%s@%s/%s" % (DB["USER"], DB["PASSWORD"], DB["HOST"], DB["NAME"])
engine = sqlalchemy.create_engine(engine_string)
Session = sqlalchemy.orm.sessionmaker(bind=engine)

AUTH_USER_MODEL = 'jambalaya.ShimUser'
LOGIN_REDIRECT_URL = "/"
# Idle timeout in seconds
SESSION_IDLE_TIMEOUT = 60 * 30

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = '/static/'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    "django.core.context_processors.request",
    "jambalaya.middleware.auth.sqlalchemy_user_context_provider"
)