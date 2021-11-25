import base64
from pathlib import Path
import os
import shutil

import dj_database_url
import environ

import saml2
import saml2.saml

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# Set up .env
ENV_FILE = os.path.join(BASE_DIR, ".env")
if os.path.exists(ENV_FILE):
    environ.Env.read_env(ENV_FILE)
env = environ.Env(
    DEBUG=(bool, False),
    XMLSEC1=(str, shutil.which("xmlsec1")),
)

BASE_URL = env("BASE_URL")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "main",
    "djangosaml2",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "djangosaml2.middleware.SamlSessionMiddleware",

]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {"default": dj_database_url.config()}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# saml config

SAML_CONFIG_DIR = os.path.join(BASE_DIR, "config", "saml")

SAML_PRIVATE_KEY_PATH = os.path.join(SAML_CONFIG_DIR, "sp.private.key")
SAML_PUBLIC_CERT_PATH = os.path.join(SAML_CONFIG_DIR, "sp.public.crt")


if env("SAML_PRIVATE_KEY", default=None) and env("SAML_PUBLIC_CERT", default=None):
    # if the key/crt are passed in as env vars => save it to a file
    with open(SAML_PRIVATE_KEY_PATH, "wb") as f:
        f.write(base64.b64decode(env("SAML_PRIVATE_KEY")))

    with open(SAML_PUBLIC_CERT_PATH, "wb") as f:
        f.write(base64.b64decode(env("SAML_PUBLIC_CERT")))

SAML_SESSION_COOKIE_NAME = "saml_session"
SESSION_COOKIE_SECURE = True

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "djangosaml2.backends.Saml2Backend",
)

LOGIN_URL = "/saml2/login/"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SAML_DEFAULT_BINDING = saml2.BINDING_HTTP_POST

SAML_DJANGO_USER_MAIN_ATTRIBUTE = "username"
SAML_USE_NAME_ID_AS_USERNAME = True
SAML_CREATE_UNKNOWN_USER = True

SAML_CONFIG = {
  # full path to the xmlsec1 binary programm
  "xmlsec_binary": env("XMLSEC1"),

  # your entity id, usually your subdomain plus the url to the metadata view
  "entityid": f"{BASE_URL}/saml2/metadata/",

  # directory with attribute mapping
  "attribute_map_dir": os.path.join(SAML_CONFIG_DIR, "attribute_maps"),

  # Permits to have attributes not configured in attribute-mappings
  # otherwise...without OID will be rejected
  "allow_unknown_attributes": True,

  # this block states what services we provide
  "service": {
      # we are just a lonely SP
      "sp" : {
          "name": "Federated Django sample SP",
          "name_id_format": saml2.saml.NAMEID_FORMAT_TRANSIENT,

          # For Okta add signed logout requets. Enable this:
          # "logout_requests_signed": True,

          "endpoints": {
              # url and binding to the assetion consumer service view
              # do not change the binding or service name
              "assertion_consumer_service": [
                  (f"{BASE_URL}/saml2/acs/",
                   saml2.BINDING_HTTP_POST),
                  ],
              # url and binding to the single logout service view
              # do not change the binding or service name
              "single_logout_service": [
                  # Disable next two lines for HTTP_REDIRECT for IDP"s that only support HTTP_POST. Ex. Okta:
                  (f"{BASE_URL}/saml2/ls/",
                   saml2.BINDING_HTTP_REDIRECT),
                  (f"{BASE_URL}/saml2/ls/post",
                   saml2.BINDING_HTTP_POST),
                  ],
              },

          "signing_algorithm":  saml2.xmldsig.SIG_RSA_SHA256,
          "digest_algorithm":  saml2.xmldsig.DIGEST_SHA256,

           # Mandates that the identity provider MUST authenticate the
           # presenter directly rather than rely on a previous security context.
          "force_authn": False,

           # Enable AllowCreate in NameIDPolicy.
          "name_id_format_allow_create": True,

           # attributes that this project need to identify a user
          "required_attributes": [],

           # attributes that may be useful to have but not required
          "optional_attributes": ["eduPersonAffiliation"],

          "want_response_signed": False,
          "authn_requests_signed": True,
          "logout_requests_signed": True,
          # Indicates that Authentication Responses to this SP must
          # be signed. If set to True, the SP will not consume
          # any SAML Responses that are not signed.
          "want_assertions_signed": True,

          "only_use_keys_in_metadata": False,

          # When set to true, the SP will consume unsolicited SAML
          # Responses, i.e. SAML Responses for which it has not sent
          # a respective SAML Authentication Request.
          "allow_unsolicited": False,

          # in this section the list of IdPs we talk to are defined
          # This is not mandatory! All the IdP available in the metadata will be considered instead.
          "idp": {
              # we do not need a WAYF service since there is
              # only an IdP defined here. This IdP should be
              # present in our metadata

          },
      },
  },
  # where the remote metadata is stored, local, remote or mdq server.
  # One metadatastore or many ...
  "metadata": {
      "local": [os.path.join(SAML_CONFIG_DIR, 'metadata.xml')],
  },

  # set to 1 to output debugging information
  "debug": 1,

  # Signing
  "key_file": SAML_PRIVATE_KEY_PATH,  # private part, loaded via env var (see above)
  "cert_file": SAML_PUBLIC_CERT_PATH,  # public part

  # Encryption
  "encryption_keypairs": [{
    "key_file": SAML_PRIVATE_KEY_PATH,  # private part, loaded via env var (see above)
    "cert_file": SAML_PUBLIC_CERT_PATH,  # public part
  }],

  # own metadata settings
  "contact_person": [
      {"given_name": "Lorenzo",
       "sur_name": "Gil",
       "company": "Yaco Sistemas",
       "email_address": "lgs@yaco.es",
       "contact_type": "technical"},
      {"given_name": "Angel",
       "sur_name": "Fernandez",
       "company": "Yaco Sistemas",
       "email_address": "angel@yaco.es",
       "contact_type": "administrative"},
      ],
  # you can set multilanguage information here
  "organization": {
      "name": [("Yaco Sistemas", "es"), ("Yaco Systems", "en")],
      "display_name": [("Yaco", "es"), ("Yaco", "en")],
      "url": [("http://www.yaco.es", "es"), ("http://www.yaco.com", "en")],
      },
  }
