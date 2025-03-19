from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-5_ovb24+ko-!t+&%%oe*4efxxxm+c&y5#itsj4m0s-5h+!y^h0'

DEBUG = True

ALLOWED_HOSTS = []

# ✅ CORS Settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # ✅ Your frontend
]
CORS_ALLOW_CREDENTIALS = True

# ✅ CSRF trusted origins for frontend
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",  # ✅ Allow CSRF from Vite frontend
]

# App and Middleware
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'twitter_app',
    'rest_framework',
    'corsheaders',  # ✅ Add corsheaders
]

AUTH_USER_MODEL = 'twitter_app.User'
LOGIN_REDIRECT_URL = '/home/'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ MUST be at top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Analytica.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Analytica.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


#Config to connect with AWS RDS
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'analytica',
#         'USER':'postgres',
#         'PASSWORD':'analytica',
#         'HOST':'database-1.cg1akyewuxpb.us-east-1.rds.amazonaws.com',
#         'PORT':'5432',
#     }
# }



AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ Keep cookies unsecured for localhost (optional in development)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
