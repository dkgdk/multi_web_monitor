import httpx
import time
from django.utils import timezone


def check_website(website):
    """
    Performs an HTTP GET request to the given Website object.
    Returns a dict with: status, response_time, status_code, error_message
    """
    start = time.monotonic()
    result = {
        'status': 'down',
        'response_time': None,
        'status_code': None,
        'error_message': None,
    }
    try:
        with httpx.Client(timeout=website.timeout, follow_redirects=True) as client:
            response = client.get(website.url)
            elapsed_ms = (time.monotonic() - start) * 1000
            result['status_code'] = response.status_code
            result['response_time'] = round(elapsed_ms, 2)
            result['status'] = 'up' if response.status_code < 400 else 'down'
    except httpx.TimeoutException:
        result['error_message'] = f"Timeout after {website.timeout}s"
        result['status'] = 'down'
    except httpx.RequestError as e:
        result['error_message'] = str(e)
        result['status'] = 'down'
    except Exception as e:
        result['error_message'] = f"Unexpected error: {str(e)}"
        result['status'] = 'error'
    return result


def run_check_for_website(website):
    """
    Runs a check, saves a MonitorCheck record, updates Website stats & status.
    Returns the MonitorCheck instance.
    """
    from monitors.models import MonitorCheck, Incident

    data = check_website(website)

    # Save check record
    check = MonitorCheck.objects.create(
        website=website,
        status=data['status'],
        response_time=data['response_time'],
        status_code=data['status_code'],
        error_message=data['error_message'],
        checked_at=timezone.now(),
    )

    # Update website stats
    website.total_checks += 1
    if data['status'] == 'up':
        website.successful_checks += 1

    prev_status = website.current_status
    website.current_status = data['status']
    website.last_checked = timezone.now()
    website.response_time = data['response_time']
    website.update_uptime()
    website.save()

    # Create incident if just went down
    if prev_status == 'up' and data['status'] == 'down':
        Incident.objects.create(
            website=website,
            title=f"{website.name} is DOWN",
            description=data['error_message'] or f"HTTP {data['status_code']}",
            severity='critical',
        )

    # Resolve incident if just came back up
    if prev_status == 'down' and data['status'] == 'up':
        Incident.objects.filter(
            website=website,
            is_resolved=False
        ).update(is_resolved=True, resolved_at=timezone.now())

    return check
