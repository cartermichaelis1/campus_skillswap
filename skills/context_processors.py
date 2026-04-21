from .models import Appointment


def pending_appointments(request):
    """Makes pending_appointment_count available in every template."""
    if request.user.is_authenticated:
        count = Appointment.objects.filter(
            skill__user=request.user,
            status='pending'
        ).count()
        return {'pending_appointment_count': count}
    return {'pending_appointment_count': 0}
