from app.models import CustomUser
from django.db.models import Count
import datetime

# Get count users joined per day
def dashboard(request):
    try:
        if request.path == '/admin/':
            # Get count users joined per day
            current_month = datetime.datetime.now().month

            # Get the number of registrations for each day in the current month
            registrations = CustomUser.objects.filter(date_joined__month=current_month).annotate(
                count=Count("id")
            ).values("date_joined__day", "count")

            new_data = []
            month_31 = [1, 3, 5, 7, 8, 10, 12]

            if current_month in month_31:
                for i in range(1, 32):
                    if i not in [x['date_joined__day'] for x in new_data]:
                        new_data.append({'date_joined__day': i, 'count': 0})
            else:
                for i in range(1, 31):
                    if i not in [x['date_joined__day'] for x in new_data]:
                        new_data.append({'date_joined__day': i, 'count': 0})

            for item in registrations:
                day = item['date_joined__day']
                count = item['count']

                for i in range(len(new_data)):
                    if new_data[i]['date_joined__day'] == day:
                        new_data[i]['count'] += count

            return {'register_data': new_data, 'current_month': current_month }
    except:
        pass
    return {}
