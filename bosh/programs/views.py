from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Program
from .forms import ProgramForm
from applications.models import Application  # Import Application model

@login_required
def program_list(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    programs = Program.objects.all()
    return render(request, 'programs/program_list.html', {'programs': programs})

@login_required
def add_program(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('program_list')
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
            return redirect('program_list')
    else:
        form = ProgramForm(instance=program)
    return render(request, 'programs/edit_program.html', {'form': form})

@login_required
def delete_program(request, program_id):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    
    program = get_object_or_404(Program, id=program_id)
    
    # Check if there are any applications for this program
    applications_exist = Application.objects.filter(program=program).exists()
    
    if request.method == 'POST':
        if applications_exist:
            messages.error(request, "This program has received applications and cannot be deleted.")
            return redirect('program_list')
        program.delete()
        messages.success(request, "Program deleted successfully.")
        return redirect('program_list')
    
    return render(request, 'programs/delete_program.html', {'program': program, 'applications_exist': applications_exist})
