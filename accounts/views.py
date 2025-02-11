import json
from django.forms import IntegerField
from django.http import HttpResponseRedirect,JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, ListView, CreateView, UpdateView, TemplateView,FormView,DetailView
from django.contrib.auth.views import LoginView,LogoutView
from django.contrib.auth import login,logout,authenticate
from .forms import *
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import JobSeekerProfile, User, EducationDetails
from .forms import UserForm, JobSeekerProfileForm, EducationDetailsFormSet
from django.db.models import Q

from django.views import View
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .models import JobSeekerProfile, User, EducationDetails
from .forms import UserForm, JobSeekerProfileForm, EducationDetailsFormSet
# Create your views here.

class HomeView(TemplateView):
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetching data for different sections
        job_posts = JobPosting.objects.filter(is_active=True).order_by('-created_at')
        
        # pagination
        paginator = Paginator(job_posts,8)  #show 10 posts per page
        page = self.request.GET.get('page')  #get current page from the query params
        jobs = paginator.get_page(page) #get jobposts for the requested page
        
        context['jobposts'] = jobs            #passing pagination in context
        return context
    
class DashView(LoginRequiredMixin,TemplateView):
    template_name = 'dashboard.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Tota_registered_users"] = User.objects.all().count()
        context["total_active_users"] = User.objects.filter(is_active=True).count()
        context["total_Active_job_posts"] = JobPosting.objects.filter(is_active=True).count()
        return context
    
      
# class JobSeekerHomeView(LoginRequiredMixin, TemplateView):
#     template_name = 'jobseeker/home.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Fetching data for different sections
#         job_posts = JobPosting.objects.filter(is_active=True).order_by('-created_at')
        
#         # pagination
#         paginator = Paginator(job_posts,10)  #show 10 posts per page
#         page = self.request.GET.get('page')  #get current page from the query params
#         jobs = paginator.get_page(page) #get jobposts for the requested page
        
#         context['jobposts'] = jobs            #passing pagination in context
#         return context


class JobSeekerHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'jobseeker/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_posts = JobPosting.objects.filter(is_active=True).order_by('-created_at')

        # Get filter parameters from request
        job_type = self.request.GET.get('job_type')
        job_category = self.request.GET.get('job_category')
        location = self.request.GET.get('location')

        # Apply filters
        if job_type:
            job_posts = job_posts.filter(job_type=job_type)
        if location:
            job_posts = job_posts.filter(
                Q(job_city__icontains=location) | 
                Q(job_state__icontains=location)
            )
        if job_category:
            job_posts = job_posts.filter(job_category = job_category)    

        context['jobposts'] = job_posts
        context['job_types'] = JobPosting.JOB_TYPE_CHOICES
        context['job_categories'] = JobPosting.JOB_CATEGORY
        return context
    

    
class AboutUsView(TemplateView):
    template_name = 'about_us.html'
    
class ContactUsView(TemplateView):
    template_name = 'contact_us.html'
    
class ErrorTemplateView(TemplateView):
    template_name = '404.html'
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ USER REGISTRATION VIEW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    
class UserRegistrationView(FormView):
    template_name = "register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy('accounts:dash_page')

    def form_valid(self, form):
        try:
            # Create the user object but don't save to database yet
            user = form.save(commit=False)
            
            # Set the hashed password
            user.set_password(form.cleaned_data['password'])
            
            # Now save the user object
            user.save()
            
            # Log the user in
            login(self.request, user)
            
            success_url = self.success_url
                
            # Return the appropriate redirect response
            return HttpResponseRedirect(success_url)
        
        except Exception as e:
            
            form.add_error(None, "An error occurred during registration.")
            return self.form_invalid(form)
        
    def form_invalid(self, form):
        # Add error handling for form validation failures
        return self.render_to_response(self.get_context_data(form=form))
        
class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True  # Redirect already logged-in users to their dashboard or landing page
    
    def get_success_url(self):
        if self.request.user.is_authenticated:
            if self.request.user.role == User.Role.JOB_SEEKER.value:
                return reverse_lazy('accounts:jobseeker_home')  # Redirect to job seeker homepage
            else:
                return reverse_lazy('accounts:dash_page')  # Redirect to dashboard for other users
        return super().get_success_url()  # Default behavior
    
    def form_invalid(self, form):
        """Handle inactive users and display custom error message"""
        email = self.request.POST.get('username')  # Get email from form input
        password = self.request.POST.get('password')

        # Try to fetch the user based on the provided email
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.error(self.request, "Your account has been blocked. Please contact the administrator.")
                return render(self.request, 'login.html', {'form': form})
        except User.DoesNotExist:
            pass  # User does not exist, continue to default error message

        # Perform normal authentication to check for incorrect credentials
        if not authenticate(self.request, username=email, password=password):
            messages.error(self.request, "Invalid username or password.")
        
        return render(self.request, 'login.html', {'form': form})

class UserLogoutView(LoginRequiredMixin,LogoutView):
    next_page = reverse_lazy('accounts:landing_page')
    
class UserJobSeekerProfileCreateView(LoginRequiredMixin,CreateView):
    model = JobSeekerProfile
    form_class = JobSeekerProfileForm
    template_name = "jobseeker/create.html"
    success_url = reverse_lazy("accounts:dash_page")

    def form_valid(self, form):
        form.instance.user = self.request.user  # Assign the logged-in user

        # Save the profile first
        response = super().form_valid(form)

        # Handle the education data JSON
        education_json = self.request.POST.get("education_data")
        if education_json:
            education_entries = json.loads(education_json)
            job_seeker_profile = self.object

            for entry in education_entries:
                EducationDetails.objects.create(
                    profile=job_seeker_profile,
                    education_data=entry
                )

        messages.success(self.request, "Profile created successfully!")
        return response
        
class JobSeekerProfileListView(LoginRequiredMixin, ListView):
    model = JobSeekerProfile
    template_name = "jobseeker/list.html"
    context_object_name = "jobseekerProfile"

    def get_queryset(self):
        """Ensure only the logged-in user's profile is returned."""
        return JobSeekerProfile.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the logged-in user's profile
        user_profile = self.get_queryset().first()
        context["jobseekerProfile"] = user_profile  # Pass the profile object
        
        # Fetch and decode education details
        if user_profile:
            education_entries = user_profile.education_detail.all()
            education_data_list = []

            for edu in education_entries:
                if isinstance(edu.education_data, str):
                    # Convert only if it's a string
                    try:
                        education_data_list.append(json.loads(edu.education_data))
                    except json.JSONDecodeError:
                        education_data_list.append({})
                else:
                    # If it's already a dictionary, use it directly
                    education_data_list.append(edu.education_data)  

            context["education_details"] = education_data_list
        else:
            context["education_details"] = None  # No education data
        
        return context
    


class JobSeekerProfileUpdateView(LoginRequiredMixin, View):
    template_name = "jobseeker/update.html"
    success_url = reverse_lazy("accounts:jobseeker_profile_list")

    def get(self, request):
        """Display the profile update form with user details."""
        user = request.user

        # Get job seeker profile
        job_seeker_profile = JobSeekerProfile.objects.get(user=user)

        # Pre-fill forms with existing data
        user_form = UserForm(instance=user)
        jobseeker_form = JobSeekerProfileForm(instance=job_seeker_profile)
        education_formset = EducationDetailsFormSet(queryset=job_seeker_profile.education_detail.all())

        return render(request, self.template_name, {
            "user_form": user_form,
            "jobseeker_form": jobseeker_form,
            "education_formset": education_formset,
        })

    def post(self, request):
        """Handle profile update form submission."""
        user = request.user
        job_seeker_profile = JobSeekerProfile.objects.get(user=user)

        # Bind forms with submitted data
        user_form = UserForm(request.POST, request.FILES, instance=user)
        jobseeker_form = JobSeekerProfileForm(request.POST, request.FILES, instance=job_seeker_profile)
        education_formset = EducationDetailsFormSet(request.POST, queryset=job_seeker_profile.education_detail.all())

        if user_form.is_valid() and jobseeker_form.is_valid() and education_formset.is_valid():
            user_form.save()
            jobseeker_form.save()
            education_formset.save()

            messages.success(request, "Your profile has been updated successfully!")
            return redirect(self.success_url)
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {
            "user_form": user_form,
            "jobseeker_form": jobseeker_form,
            "education_formset": education_formset,
        })

    
#~~~~~~~~~~~~~~~~~~~~ Organisation REGISTRATION VIEW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class EmployerOrganisationRegisterView(LoginRequiredMixin,CreateView):
    model = OrganisationRegister
    form_class = OrganisationRegistrationForm
    template_name = "organisations/create.html"
    success_url = reverse_lazy("accounts:employer_organisation_list")
    
    def dispatch(self, request, *args, **kwargs):
        # Check if user already has an organization
        if hasattr(request.user, 'organisation'):
            messages.warning(request, 'You already have a registered organization.')
            return redirect('accounts:employer_organisation_list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)  # This saves the form
        messages.success(self.request, 'Organization registered successfully!')
        return response
    
    def form_invalid(self, form):
        # Re-render the form with validation errors
        messages.error(self.request, 'Please correct the errors below.')
        return self.render_to_response(self.get_context_data(form=form))
    
class EmployerOrganisationListView(LoginRequiredMixin,ListView):
    model = OrganisationRegister
    template_name = "organisations/list.html"
    context_object_name = "organisations"
    
    def get_queryset(self):
        # Only show the organization belonging to the current user
        return OrganisationRegister.objects.filter(user=self.request.user)
    
class EmployerOrganisationUpdateView(LoginRequiredMixin, UpdateView):
    model = OrganisationRegister
    form_class = OrganisationRegistrationForm
    template_name = "organisations/edit.html"  # Using the same template as CreateView
    success_url = reverse_lazy("accounts:employer_organisation_list")
    
    def test_func(self):
        # Ensure user can only edit their own organization
        org = self.get_object()
        return org.user == self.request.user

    def get_object(self, queryset=None):
        # Get the organization for the current user
        return get_object_or_404(OrganisationRegister, user=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)  # This saves the form
        messages.success(self.request, "Organization details updated successfully!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)
    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ SUPER ADMIN VIEW ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserListView(View):
    template_name = 'super_admin/total_user.html'
    
    def get(self, request):
        role_filter = request.GET.get('role')
        valid_roles = [choice[0] for choice in User.Role.choices()]

        # Filter users based on role (default: Employers + Job Seekers)
        if role_filter in valid_roles:
            users = User.objects.filter(role=role_filter)
        else:
            users = User.objects.filter(role__in=[User.Role.EMPLOYER.value, User.Role.JOB_SEEKER.value])

        context = {
            'users': users,
            'current_role': role_filter if role_filter in valid_roles else 'all',
            'role_choices': User.Role.choices(),
        }
        return render(request, 'super_admin/total_user.html', context)

class ToggleUserStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.POST.get("user_id")
            is_active = request.POST.get("is_active") == "true"
            
            user = get_object_or_404(User, id=user_id)

            # Prevent self-deactivation
            if user == request.user:
                return JsonResponse({
                    "success": False, 
                    "error": "You cannot deactivate your own account"
                })

            # Prevent deactivating super admins
            if user.is_superuser:
                return JsonResponse({
                    "success": False, 
                    "error": "Cannot deactivate super admin"
                })

            user.is_active = is_active
            user.save()
            
            return JsonResponse({
                "success": True, 
                "message": f"User {user.username} status updated successfully.",
                "new_status": "Active" if is_active else "Inactive"
            })

        except Exception as e:
            return JsonResponse({
                "success": False, 
                "error": str(e)
            }, status=500)

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'super_admin/user_detail.html'
    context_object_name = 'user_details'

    def test_func(self):
        return self.request.user.is_superuser    
    
class SuperUserProfileUpdateView(LoginRequiredMixin,UpdateView):
    template_name = "super_admin/user_profile_edit.html"
    success_url = reverse_lazy("accounts:jobseeker_profile_list")

    def get(self, request):
        """Display the profile update form with user details."""
        user = request.user

        # Pre-fill forms with existing data
        user_form = UserForm(instance=user)

        return render(request, self.template_name, {
            "user_form": user_form,
        })

    def post(self, request):
        """Handle profile update form submission."""
        user = request.user

        # Bind forms with submitted data
        user_form = UserForm(request.POST, request.FILES, instance=user)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect(self.success_url)
        else:
            messages.error(request, "Please correct the errors below.")

        return render(request, self.template_name, {
            "user_form": user_form
        })
        
class SuperUserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "super_admin/user_profile.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Retrieve the logged-in super user's data based on their role
        # assuming 'role' is a field in the User model
        if self.request.user.role == '1':  # Check if user is a superuser
            super_user = User.objects.get(id=self.request.user.id)
            context["super_user"] = super_user
        else:
            context["error_message"] = "You do not have permission to view this page."
        
        return context
    
# <!---------------------------------- JOB POSTING ---------------------

class EmployerJobPostCreateView(LoginRequiredMixin, CreateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'job_post/create.html'
    success_url = reverse_lazy('accounts:employer_job_post_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Check if the user has an organisation
        if not hasattr(self.request.user, 'organisation'):
            messages.error(request, "You must be associated with an organisation to post a job.")
            return redirect('accounts:employer_dashboard')  # Redirect to a relevant page
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.organisation = self.request.user.organisation  # Assign the organisation
        return super().form_valid(form)
    
class EmployerJobPostListView(LoginRequiredMixin, ListView):
    model = JobPosting
    template_name = 'job_post/employer_jobs.html'
    context_object_name = 'employee_jobs'
    
    def get_queryset(self):
        return JobPosting.objects.filter(user = self.request.user).order_by('-created_at')
    
class JobPostingDetailView(LoginRequiredMixin, DetailView):
    model = JobPosting
    template_name = "job_post/job_posting_detail.html"
    context_object_name = "job"
    
class EmployerJobPostUpdateView(LoginRequiredMixin, UpdateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = "job_post/create.html"
    success_url = reverse_lazy("accounts:employer_job_post_list")

    def test_func(self):
        organisation = self.get_object()
        return organisation.user == self.request.user  # Only allow if the user owns this org

    def form_valid(self, form):
        messages.success(self.request, "Organization details updated successfully!")
        return redirect('accounts:employer_job_post_list')

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return redirect('accounts:edit_organisation')
    
class EmployerJobPostDeleteView(LoginRequiredMixin, DeleteView):
    model = JobPosting
    success_url = reverse_lazy('accounts:employer_job_post_list')
    
    
# view for the jobseeker for viewing the detailed view of the job posts 
class JobSeekerJobDetailView(LoginRequiredMixin, DetailView):
    model = JobPosting
    template_name = 'jobseeker/job_detail.html'
    context_object_name = 'jobsdetail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the current job seeker already applied:
        if hasattr(self.request.user, 'job_seeker_profile'):
            context['has_applied'] = JobApplication.objects.filter(
                job_posting=self.object,
                job_seeker_profile=self.request.user.job_seeker_profile
            ).exists()
        return context
    
class JobApplicationSubmitView(LoginRequiredMixin,CreateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = 'jobseeker/job_application_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Ensure only job seekers can apply
        if not hasattr(request.user, 'job_seeker_profile'):
            print("sfhfksjfskjfsnk")
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        # Set the foreign keys
        job = get_object_or_404(JobPosting, pk=self.kwargs.get('job_pk'))
        print(job)
        form.instance.job_posting = job
        form.instance.job_seeker_profile = self.request.user.job_seeker_profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('accounts:job_application_list')
    
    
class JobSeekerApplicationsListView(LoginRequiredMixin,ListView):
        model = JobApplication
        template_name = 'jobseeker/job_application_list.html'
        context_object_name = 'applications'
        
        def get_queryset(self):
            return JobApplication.objects.filter(
                job_seeker_profile = self.request.user.job_seeker_profile
            ).order_by('-applied_at')
            
# <----------------- employer side handling of job application  ===============
            
class ApplicationList(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = 'job_post/application_list.html'
    context_object_name = 'applications'

    def test_func(self):
        return self.request.user.role == User.Role.EMPLOYER.value

    def get_queryset(self):
        job_posting = get_object_or_404(JobPosting, id=self.kwargs['pk'])
        return JobApplication.objects.filter(
            job_posting=job_posting,
            job_posting__organisation=self.request.user.organisation
        ).order_by('-applied_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job_posting'] = get_object_or_404(JobPosting, id=self.kwargs['pk'])
        return context

class ApplicationDetailUpdateView(LoginRequiredMixin, UpdateView):
    model = JobApplication
    fields = ['status']  # Only update status
    template_name = 'job_post/application_detail.html'
    context_object_name = 'application'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Ensure that the logged-in employer owns this application
        if request.user.organisation != self.object.job_posting.organisation:
            return self.handle_no_permission()
        # Mark the application as viewed if not already done
        if not self.object.employer_viewed:
            self.object.employer_viewed = True
            self.object.save(update_fields=['employer_viewed'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch job seeker profile
        job_seeker_profile = self.object.job_seeker_profile
        context["job_seeker_profile"] = job_seeker_profile

        # Fetch education details
        if job_seeker_profile:
            education_entries = job_seeker_profile.education_detail.all()
            education_data_list = []

            for edu in education_entries:
                if isinstance(edu.education_data, str):
                    try:
                        education_data_list.append(json.loads(edu.education_data))  # Convert JSON string to dict
                    except json.JSONDecodeError:
                        education_data_list.append({})
                else:
                    education_data_list.append(edu.education_data)  # Use as-is if already a dict
            
            context["education_details"] = education_data_list
        else:
            context["education_details"] = None  # No education data available

        return context


    def get_success_url(self):
        # Redirect back to the same page after a successful update.
        return reverse_lazy('accounts:application_detail_update', kwargs={'pk': self.object.pk})