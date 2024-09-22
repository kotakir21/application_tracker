from django.shortcuts import render, redirect, get_object_or_404
from applications.models import Application, ApplicationStatus, Comment
from programs.models import Program
from programs.forms import ProgramForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from applications.forms import ProgramApplicationForm, ApplicationStatusForm, AdditionalDocumentsForm, CommentForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from custom_user.models import User
from django.urls import reverse

@login_required
def user_dashboard(request):
    profile = request.user.profile
    applications = request.user.applications.all().order_by('-date_of_application')
    programs = Program.objects.all()

    return render(request, 'dashboard/user_dashboard.html', {
        'profile': profile,
        'applications': applications,
        'programs': programs,
    })

@login_required
def officer_dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied("You do not have permission to access this page.")

    profile = request.user.profile
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-date_of_application')
    program_filter = request.GET.get('program', '')

    applications = Application.objects.all()

    if search_query:
        applications = applications.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if program_filter:
        applications = applications.filter(program__name__icontains=program_filter)

    applications = applications.order_by(sort_by)
    programs = Program.objects.all()

    return render(request, 'dashboard/officer_dashboard.html', {
        'profile': profile,
        'applications': applications,
        'programs': programs,
        'search_query': search_query,
        'program_filter': program_filter,
        'sort_by': sort_by,
    })

@login_required
def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    comments = application.comments.filter(parent=None)
    
    # Fetch or generate timeline events (status updates, document uploads, etc.)
    timeline_events = application.get_timeline_events()  # This pulls events from the Application model

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.application = application
            comment.save()

            # No need to create a TimelineEvent, since events are aggregated in get_timeline_events()

            # Send comment notification email
            send_comment_notification(comment, request)

            return redirect('application_detail', application_id=application.id)
    else:
        comment_form = CommentForm()

    return render(request, 'dashboard/application_detail.html', {
        'application': application,
        'comments': comments,
        'comment_form': comment_form,
        'timeline_events': timeline_events,  # Pass the timeline events to the template
    })


@login_required
def edit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if application.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to edit this application.")

    if request.method == 'POST':
        form = ProgramApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()

            # Record a timeline event
            TimelineEvent.objects.create(
                application=application,
                event_type='Application Updated',
                description=f'{request.user.get_full_name()} updated the application.',
            )

            # Send application edit notification email
            send_application_edit_notification(application, request)

            return redirect('user_dashboard' if not request.user.is_staff else 'officer_dashboard')
    else:
        form = ProgramApplicationForm(instance=application)

    return render(request, 'dashboard/edit_application.html', {
        'form': form,
    })

@login_required
def delete_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if application.user != request.user and not request.user.is_staff:
        raise PermissionDenied("You do not have permission to delete this application.")

    if request.method == 'POST':
        application.delete()

        # Record a timeline event
        TimelineEvent.objects.create(
            application=application,
            event_type='Application Deleted',
            description=f'{request.user.get_full_name()} deleted the application.',
        )

        return redirect('user_dashboard' if not request.user.is_staff else 'officer_dashboard')

    return render(request, 'dashboard/delete_application.html', {
        'application': application,
    })

@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if not request.user.is_staff:
        raise PermissionDenied("You do not have permission to update the status of this application.")

    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application.current_status)
        if form.is_valid():
            new_status = form.save(commit=False)
            new_status.application = application
            new_status.officer = request.user
            new_status.save()
            application.current_status = new_status
            application.status = new_status.status
            application.save()

            # Record a timeline event
            TimelineEvent.objects.create(
                application=application,
                event_type='Status Updated',
                description=f'Status updated to {new_status.status} by {request.user.get_full_name()}.',
            )

            # Send status update notification email
            send_status_update_notification(application, request)

            return redirect('application_detail', application_id=application.id)
    else:
        form = ApplicationStatusForm(instance=application.current_status)

    return render(request, 'dashboard/update_application_status.html', {
        'form': form,
        'application': application,
    })

@login_required
def upload_additional_documents(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    if not request.user.is_staff and application.user != request.user:
        raise PermissionDenied("You do not have permission to upload documents for this application.")

    if request.method == 'POST':
        form = AdditionalDocumentsForm(request.POST, request.FILES, instance=application.current_status)
        if form.is_valid():
            status = form.save(commit=False)
            status.application = application
            status.officer = request.user
            status.additional_documents_required = False
            status.save()

            # Record a timeline event
            TimelineEvent.objects.create(
                application=application,
                event_type='Document Uploaded',
                description=f'{request.user.get_full_name()} uploaded additional documents.',
            )

            # Send document upload notification email
            send_document_upload_notification(application, request)

            return redirect('application_detail', application_id=application.id)
    else:
        form = AdditionalDocumentsForm(instance=application.current_status)

    return render(request, 'dashboard/upload_documents.html', {
        'form': form,
        'application': application,
    })

@login_required
def add_program(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()

            # Record a timeline event (if applicable)
            TimelineEvent.objects.create(
                application=None,
                event_type='Program Added',
                description=f'Program {program.name} was added by {request.user.get_full_name()}.',
            )

            # Send program added notification email
            send_program_added_notification(program, request)

            return redirect('officer_dashboard')
    else:
        form = ProgramForm()

    return render(request, 'programs/add_program.html', {'form': form})

@login_required
def edit_program(request, program_id):
    if not request.user.is_staff:
        return redirect('user_dashboard')

    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()

            # Record a timeline event (if applicable)
            TimelineEvent.objects.create(
                application=None,
                event_type='Program Edited',
                description=f'Program {program.name} was edited by {request.user.get_full_name()}.',
            )

            return redirect('officer_dashboard')
    else:
        form = ProgramForm(instance=program)

    return render(request, 'programs/edit_program.html', {'form': form})

@login_required
def delete_program(request, program_id):
    if not request.user.is_staff:
        return redirect('user_dashboard')

    program = get_object_or_404(Program, id=program_id)

    if request.method == 'POST':
        program.delete()

        # Record a timeline event (if applicable)
        TimelineEvent.objects.create(
            application=None,
            event_type='Program Deleted',
            description=f'Program {program.name} was deleted by {request.user.get_full_name()}.',
        )

        return redirect('officer_dashboard')

    return render(request, 'programs/delete_program.html', {'program': program})

# Email Notification Functions

def send_application_edit_notification(application, request):
    subject = f"Your Application for {application.program.name} Has Been Updated"
    edit_url = request.build_absolute_uri(reverse('application_detail', args=[application.id]))
    message = render_to_string('emails/application_edit_notification.html', {
        'application': application,
        'edit_url': edit_url,
    })
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [application.user.email], html_message=message)

def send_status_update_notification(application, request):
    subject = f"Application Status Updated: {application.program.name}"
    status_url = request.build_absolute_uri(reverse('application_detail', args=[application.id]))
    message = render_to_string('emails/status_update.html', {
        'application': application,
        'status_url': status_url,
    })
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [application.user.email], html_message=message)

def send_document_upload_notification(application, request):
    subject = f"New Document Uploaded for {application.program.name}"
    document_url = request.build_absolute_uri(reverse('application_detail', args=[application.id]))
    message = render_to_string('emails/document_upload.html', {
        'application': application,
        'document_url': document_url,
    })
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [application.user.email], html_message=message)

def send_comment_notification(comment, request):
    subject = f"New Comment on Your Application for {comment.application.program.name}"
    comment_url = request.build_absolute_uri(reverse('application_detail', args=[comment.application.id]))
    message = render_to_string('emails/new_comment.html', {
        'comment': comment,
        'comment_url': comment_url,
    })
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [comment.application.user.email], html_message=message)

def send_program_added_notification(program, request):
    subject = f"New Program Added: {program.name}"
    program_url = request.build_absolute_uri(reverse('apply_for_program', args=[program.id]))
    message = render_to_string('emails/new_program.html', {
        'program': program,
        'program_url': program_url,
    })
    users = User.objects.filter(is_active=True)
    emails = [user.email for user in users]
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, emails, html_message=message)
