from pathlib import Path
from datetime import timedelta
import os
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # my apps
    "accounts",
    "stores",
    "products",
    "orders",
    "payments",
    "seller_dashboard",
    # "whatsapp_bot",
    # 3rd party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "corsheaders",
    "cloudinary",
    "cloudinary_storage",
]

MIDDLEWARE = [
    # for accounts
    "accounts.middleware.JWTRefreshMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # for cors
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "accounts/templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# local db
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# prod db
DATABASE_URL = config("DATABASE_URL")
default_db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=600)

DATABASES = {
    "default": default_db_config,
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/


STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.CustomJWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_COOKIE": "access_token",  # Cookie name for access token
    "AUTH_COOKIE_REFRESH": "refresh_token",  # Cookie name for refresh token
    "AUTH_COOKIE_DOMAIN": None,  #  Change this in production
    "AUTH_COOKIE_SECURE": True,  # Only send cookies over HTTPS
    "AUTH_COOKIE_HTTP_ONLY": True,  # Protect cookies from JavaScript access
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": "none",
    "SIGNING_KEY": SECRET_KEY,
}
AUTH_USER_MODEL = "accounts.User"

# smtp
MAILERSEND_API_KEY = config("MAILERSEND_API_KEY")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
MAILERSEND_SMTP_PORT = 587
MAILERSEND_SMTP_USERNAME = "MS_LXk4IG@trial-3yxj6lj8385gdo2r.mlsender.net"
MAILERSEND_SMTP_HOST = "smtp.mailersend.net"
DEFAULT_FROM_EMAIL = "damy@trial-3yxj6lj8385gdo2r.mlsender.net"

SITE_ID = 1

# celery docker redis works on local
# CELERY_BROKER_URL = "redis://localhost:6379/0"
# CELERY_RESULT_BACKEND = "redis://localhost:6379/0"


# render redis

# CELERY_BROKER_URL = "redis://red-cukvpr23esus73b1art0:6379/0"
# CELERY_RESULT_BACKEND = "redis://red-cukvpr23esus73b1art0:6379/0"

# CELERY_ACCEPT_CONTENT = ["json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"
# CELERY_TIMEZONE = "UTC"


# cors
CORS_ALLOW_ALL_ORIGINS = True

# CORS_ALLOWED_ORIGINS = [
#     "https://your-frontend.vercel.app",
#     # Include any other domains you need
# ]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_CREDENTIALS = True


# JAZZMIN_UI_TWEAKS = {
#     "theme": "darkly",  # Try "cerulean", "cosmo", "cyborg", "darkly", etc.
#     # "dark_mode_theme": "solar",
#     "navbar_small_text": False,
#     "body_small_text": False,
#     "sidebar_nav_compact_style": False,
# }

JAZZMIN_SETTINGS = {
    "site_title": "EcomX",
    "site_header": "EcomX Admin",
    "site_brand": "EcomX",
    "welcome_sign": "Welcome to  EcomX Admin Dashboard",
    # "site_logo": "static/images/logo.png",  # Path to your logo
    "copyright": "EcomX Ltd",
    # "search_model": ["users.User", "investments.Investment"],  # Models to search
    # "user_avatar": "profile.image",  # Field for user avatars
}


# celery docker redis works on local
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"


# Use Cloudinary for default file storage
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Cloudinary configuration (replace with your credentials)
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUD_NAME"),
    "API_KEY": config("API_KEY"),
    "API_SECRET": config("API_SECRET"),
}

import cloudinary

cloudinary.config(
    cloud_name=config("CLOUD_NAME"),
    api_key=config("API_KEY"),
    api_secret=config("API_SECRET"),
    secure=True,
)
