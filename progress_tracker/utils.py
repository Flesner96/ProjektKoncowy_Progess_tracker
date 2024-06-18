from django.contrib.auth.decorators import user_passes_test


def is_superuser(user):
    return user.is_superuser

def superuser_required(view_func):
    return user_passes_test(is_superuser)(view_func)