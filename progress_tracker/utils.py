from django.contrib.auth.decorators import user_passes_test


def is_superuser(view_func):
    decorated_view_func = user_passes_test(lambda u: u.is_superuser)(view_func)
    return decorated_view_func