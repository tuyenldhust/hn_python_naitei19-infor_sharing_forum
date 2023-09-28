from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
import os

@login_required(login_url='/account/signin/')
def upload_avatar(request):
  data = {
    'files': []
  }

  if request.method == 'POST':
    if request.user.username != request.POST['username']:
      data['files'].append({
        'error': _('Cannot upload avatar for other users')
      })
      return JsonResponse(data, safe=True)
    
    # Check if the file is an image, gif or video
    if request.FILES['avatar'].content_type not in ['image/jpeg', 'image/png', 'image/gif', 'video/mp4']:
      data['files'].append({
        'error': _('File type is not supported')
      })
      return JsonResponse(data, safe=True)
    
    # Check if the file size is less than 3MB
    if request.FILES['avatar'].size > 3 * 1024 * 1024:
      data['files'].append({
        'error': _('File size is too large')
      })
      return JsonResponse(data, safe=True)      
    
    # make temporary folder if not exist
    if not os.path.exists('static/tmp/'):
      os.makedirs('static/tmp/')
    
    # Save the file to temporary folder
    with open('static/tmp/' + request.FILES['avatar'].name, 'wb+') as destination:
      for chunk in request.FILES['avatar'].chunks():
        destination.write(chunk)

    data['files'].append({
      'url': '/static/tmp/' + request.FILES['avatar'].name
    })

  return JsonResponse(data, safe=True)
