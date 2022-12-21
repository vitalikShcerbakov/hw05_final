from datetime import datetime
from django.utils import timezone

def year(request):
    return {
        'year': timezone.now().year
    }
