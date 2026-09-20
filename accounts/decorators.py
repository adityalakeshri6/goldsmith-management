from django.contrib.auth.decorators import user_passes_test


def goldsmith_required(view_func):
    """Restrict a view to users with role='goldsmith' (the shop/admin side)."""
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_goldsmith,
        login_url='accounts:login'
    )(view_func)
