from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProgramApplicationForm, ApplicationStatusForm, AdditionalDocumentsForm
from .models import Application, ApplicationStatus, Comment
from programs.models import Program
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from custom_user.models import User
from django.urls import reverse

@login_required
def apply_for_program(request, program_id):
    program = get_object_or_404(Program, id=program_id)

    # Check if the user has already applied for this program
    if Application.objects.filter(user=request.user, program=program).exists():
        return render(request, 'applications/apply.html', {
            'error': 'You have already applied for this program.',
            'program': program,
        })
    
    # Check if there are spots left
    if program.available_spots <= 0:
        return render(request, 'applications/apply.html', {
            'error': 'This program is full. No spots left.',
            'program': program,
        })

    if request.method == 'POST':
        form = ProgramApplicationForm(request.POST, request.FILES, user=request.user, program=program)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.program = program  # Link the application to the selected program
            application.save()

            # Reduce the number of available spots
            program.available_spots -= 1
            program.save()

            # Send notification emails
            send_application_submission_email(application, request)

            return redirect('user_dashboard')
        else:
            print(f"Form is not valid: {form.errors}")  # Debugging line to print form errors
    else:
        form = ProgramApplicationForm(user=request.user, program=program)

    return render(request, 'applications/apply.html', {
        'form': form,
        'program': program,
        'errors': form.errors,  # Pass the errors to the template
    })

@login_required
def edit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    program = application.program

    if request.method == 'POST':
        form = ProgramApplicationForm(request.POST, request.FILES, instance=application, user=request.user, program=program)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard')
        else:
            print(f"Form is not valid: {form.errors}")  # Debugging line to print form errors
    else:
        form = ProgramApplicationForm(instance=application, user=request.user, program=program)

    return render(request, 'applications/edit_application.html', {
        'form': form,
        'program': program,
        'errors': form.errors,  # Pass the errors to the template
    })

@login_required
def delete_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    program = application.program

    if request.method == 'POST':
        application.delete()
        # Increase the number of available spots
        program.available_spots += 1
        program.save()
        return redirect('user_dashboard')

    return render(request, 'applications/delete_application.html', {
        'application': application,
    })

@login_required
def application_detail(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    timeline_events = application.get_timeline_events()
    return render(request, 'applications/application_detail.html', {
        'application': application,
        'timeline_events': timeline_events,
    })

def send_application_submission_email(application, request):
    subject = f"New Application Submitted for {application.program.name}"
    
    # For applicant
    applicant_url = request.build_absolute_uri(reverse('application_detail', args=[application.id]))
    applicant_message = render_to_string('emails/application_submission_applicant.html', {
        'application': application,
        'applicant_url': applicant_url,
    })
    
    # For officers
    officer_url = request.build_absolute_uri(reverse('application_detail', args=[application.id]))
    officer_message = render_to_string('emails/application_submission_officer.html', {
        'application': application,
        'officer_url': officer_url,
    })

    # Send email to applicant
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, [application.user.email], html_message=applicant_message)

    # Send email to officers
    officer_emails = [officer.email for officer in User.objects.filter(is_staff=True)]
    send_mail(subject, '', settings.DEFAULT_FROM_EMAIL, officer_emails, html_message=officer_message)
