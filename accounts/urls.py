from django.urls import path, re_path
from .views import *

app_name = 'accounts'

# handler404 = 'accounts.views.error_404_view'

urlpatterns = [
    path('',HomeView.as_view(),name='landing_page'),
    path('login-page/',UserLoginView.as_view(),name='login_page'),                #login page
    path('register-page/',UserRegistrationView.as_view(),name='register_page'),   #registration pageregistration page
    
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('dash-page/',DashView.as_view(),name='dash_page'),                       #dashboard page
    path('contact-us-page/',ContactUsView.as_view(),name='contact_us_page'),        
    path('about-us-page/',AboutUsView.as_view(),name='about_us_page'),
    # re_path(r'^(?!dj-admin/).*$', ErrorTemplateView.as_view(), name='404'),
    
    path('admin-total-users/', UserListView.as_view(), name='admin_total_users'),
    path("toggle-user-status/", ToggleUserStatusView.as_view(), name="toggle_user_status"),
    path('user-detail/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path("user-profile-update/", SuperUserProfileUpdateView.as_view(), name="super_profile_update"),
    path("profile/", SuperUserProfileView.as_view(), name="super_profile"),
    
    path('employer-organisation-list/', EmployerOrganisationListView.as_view(), name='employer_organisation_list'),
    path('employer-organisation-register/', EmployerOrganisationRegisterView.as_view(), name='employer_organisation_resgister'),
    path("employer-organisation-edit/<int:pk>/", EmployerOrganisationUpdateView.as_view(), name="edit_organisation"),
    path("employer-profile/", EmployerProfileView.as_view(), name="employer_profile"),
    path("update-employer-profile/", EmployerProfileUpdateView.as_view(), name="update_employer_profile"),
    
    # employer job post
    path("employer-job-post-create/", EmployerJobPostCreateView.as_view(), name="employer_job_post_create"),
    path("employer-job-post-list/", EmployerJobPostListView.as_view(), name="employer_job_post_list"),
    path("employer-job-post-detail/<int:pk>/", JobPostingDetailView.as_view(), name='job_post_detail'),
    path("employer-job-post-update/<int:pk>/", EmployerJobPostUpdateView.as_view(), name="employer_job_post_update"),
    path("employer-job-post-delete/<int:pk>/", EmployerJobPostDeleteView.as_view(), name="employer_job_post_delete"),
    
    # Employer side URLs:
    path('employer-jobs/<int:pk>/', ApplicationList.as_view(), name='application_list'),
    path('application/<int:pk>/', ApplicationDetailUpdateView.as_view(), name='application_detail_update'),

    
    # <!---------- jobseeker section ------------------>
    
    path('jobseeker-home/',JobSeekerHomeView.as_view(),name='jobseeker_home'),
    path('jobseeker-profile-create/',UserJobSeekerProfileCreateView.as_view(),name='jobseeker_profile_create'),
    path('jobseeker-profile-list/',JobSeekerProfileListView.as_view(),name='jobseeker_profile_list'),
    path("jobseeker-profile-update/", JobSeekerProfileUpdateView.as_view(), name="jobseeker_profile_update"),
    
    path('job/<int:pk>/', JobSeekerJobDetailView.as_view(), name='job_posting_detail'),
    path('job/<int:job_pk>/apply/', JobApplicationSubmitView.as_view(), name='job_application_submit'),
    path('my-applications/', JobSeekerApplicationsListView.as_view(), name='job_application_list'),
]