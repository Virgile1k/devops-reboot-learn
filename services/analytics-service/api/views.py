from django.http import JsonResponse


def health(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'analytics-service',
        'stack': 'Django',
    })


def reports(request):
    return JsonResponse({
        'service': 'analytics-service',
        'reports': [
            {'id': 1, 'name': 'monthly-sales', 'value': 12500},
            {'id': 2, 'name': 'active-users', 'value': 340},
        ],
    })
