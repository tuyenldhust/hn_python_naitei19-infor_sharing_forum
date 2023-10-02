import re
from .models import Notification, Post

def get_notification(request):
    if request.user.is_authenticated:
        # Chech request.path not start '/admin/' with regex
        if not re.match(r'^/admin/(.*)', request.path):
            notifications=Notification.objects.filter(receive_user=request.user).order_by('-time')

            # Check notification is all readed
            if notifications.filter(is_read=False).exists():
                return dict(
                    notifications=notifications,
                    unread=True
                    )
            else:
                return dict(
                    notifications=notifications,
                    unread=False
                    )
    return dict()
