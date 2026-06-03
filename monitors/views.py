from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import timedelta

from .models import Website, MonitorCheck, Incident
from .forms import WebsiteForm
from .checker import run_check_for_website


def dashboard(request):
    """Main dashboard view."""
    websites = Website.objects.all()
    total = websites.count()
    up_count = websites.filter(current_status='up').count()
    down_count = websites.filter(current_status='down').count()
    unknown_count = websites.filter(current_status='unknown').count()

    # Recent incidents
    recent_incidents = Incident.objects.filter(
        is_resolved=False
    ).select_related('website')[:5]

    # Recent checks across all sites (last 24h)
    since = timezone.now() - timedelta(hours=24)
    recent_checks = MonitorCheck.objects.filter(
        checked_at__gte=since
    ).select_related('website').order_by('-checked_at')[:20]

    # Average response time
    avg_response = MonitorCheck.objects.filter(
        status='up',
        checked_at__gte=since,
        response_time__isnull=False
    ).aggregate(avg=Avg('response_time'))['avg'] or 0

    overall_uptime = 0
    if total > 0:
        overall_uptime = round(
            sum(w.uptime_percentage for w in websites) / total, 2
        )

    context = {
        'websites': websites,
        'total': total,
        'up_count': up_count,
        'down_count': down_count,
        'unknown_count': unknown_count,
        'recent_incidents': recent_incidents,
        'recent_checks': recent_checks,
        'avg_response': round(avg_response, 2),
        'overall_uptime': overall_uptime,
    }
    return render(request, 'monitors/dashboard.html', context)


def website_detail(request, pk):
    """Detail view for a single website with history."""
    website = get_object_or_404(Website, pk=pk)

    since = timezone.now() - timedelta(hours=24)
    checks_24h = website.checks.filter(checked_at__gte=since).order_by('checked_at')

    # Chart data: response time over last 24h
    chart_labels = []
    chart_data = []
    for check in checks_24h:
        chart_labels.append(check.checked_at.strftime('%H:%M'))
        chart_data.append(check.response_time or 0)

    # Last 50 checks for history table
    recent_checks = website.checks.all()[:50]

    # Incidents
    incidents = website.incidents.all()[:10]

    context = {
        'website': website,
        'recent_checks': recent_checks,
        'incidents': incidents,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'checks_24h_count': checks_24h.count(),
        'uptime_24h': calculate_uptime(checks_24h),
    }
    return render(request, 'monitors/website_detail.html', context)


def calculate_uptime(checks_qs):
    total = checks_qs.count()
    if total == 0:
        return 0.0
    up = checks_qs.filter(status='up').count()
    return round((up / total) * 100, 2)


def website_add(request):
    """Add a new website to monitor."""
    if request.method == 'POST':
        form = WebsiteForm(request.POST)
        if form.is_valid():
            website = form.save()
            messages.success(request, f'✓ "{website.name}" is now being monitored.')
            # Run initial check
            run_check_for_website(website)
            return redirect('monitors:dashboard')
    else:
        form = WebsiteForm()
    return render(request, 'monitors/website_form.html', {'form': form, 'action': 'Add'})


def website_edit(request, pk):
    """Edit an existing website."""
    website = get_object_or_404(Website, pk=pk)
    if request.method == 'POST':
        form = WebsiteForm(request.POST, instance=website)
        if form.is_valid():
            form.save()
            messages.success(request, f'✓ "{website.name}" updated successfully.')
            return redirect('monitors:dashboard')
    else:
        form = WebsiteForm(instance=website)
    return render(request, 'monitors/website_form.html', {'form': form, 'action': 'Edit', 'website': website})


@require_POST
def website_delete(request, pk):
    """Delete a website."""
    website = get_object_or_404(Website, pk=pk)
    name = website.name
    website.delete()
    messages.success(request, f'🗑 "{name}" removed from monitoring.')
    return redirect('monitors:dashboard')


@require_POST
def website_check_now(request, pk):
    """Manually trigger a check for a website."""
    website = get_object_or_404(Website, pk=pk)
    check = run_check_for_website(website)
    return JsonResponse({
        'status': check.status,
        'response_time': check.response_time,
        'status_code': check.status_code,
        'error_message': check.error_message,
        'checked_at': check.checked_at.isoformat(),
        'uptime': website.uptime_percentage,
    })


def incidents_list(request):
    """All incidents view."""
    open_incidents = Incident.objects.filter(is_resolved=False).select_related('website')
    resolved_incidents = Incident.objects.filter(is_resolved=True).select_related('website')[:50]
    return render(request, 'monitors/incidents.html', {
        'open_incidents': open_incidents,
        'resolved_incidents': resolved_incidents,
    })


def api_status(request):
    """JSON API endpoint returning all website statuses."""
    websites = Website.objects.all()
    data = []
    for w in websites:
        data.append({
            'id': w.id,
            'name': w.name,
            'url': w.url,
            'status': w.current_status,
            'uptime': w.uptime_percentage,
            'response_time': w.response_time,
            'last_checked': w.last_checked.isoformat() if w.last_checked else None,
        })
    return JsonResponse({'websites': data, 'timestamp': timezone.now().isoformat()})
