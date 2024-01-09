from django.contrib.auth import get_user

def user_authentication(request):
    # Add 'user' and 'is_authenticated' to the context
    user = get_user(request)
    return {'user': user, 'is_authenticated': user.is_authenticated}


