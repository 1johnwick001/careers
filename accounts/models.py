from enum import Enum
from django.db import models
from django.forms import ValidationError
from django_countries.fields import CountryField
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models import JSONField



class UserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError("The Email field can not be empty")
        if not username:
            raise ValueError("The Username field can not be empty")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, first_name, last_name, password=None):
        user = self.create_user(email, username, first_name, last_name, password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.role = User.Role.SUPER_ADMIN.value
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    class Role(Enum):
        SUPER_ADMIN = '1'
        EMPLOYER = '2'
        JOB_SEEKER = '3'
       
        @classmethod
        def choices(cls):
            return [(role.value, role.name.replace('_', ' ').title()) for role in cls]
   
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer_Not_to_Say', 'Prefer Not to Say')
    ]
   
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True, max_length=21)
    first_name = models.CharField(max_length=21)
    last_name = models.CharField(max_length=21)
    role = models.CharField(max_length=2, choices=Role.choices(), default=Role.JOB_SEEKER.value)
    country_code = CountryField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=25, choices=GENDER_CHOICES, null=True, blank=True)
    user_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
   
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
   
    objects = UserManager()
   
    def __str__(self):
        return f"{self.username} ({self.email})"
   
    def has_perm(self, perm, obj=None):
        return self.is_admin or self.is_superuser
   
    def has_module_perms(self, app_label):
        return self.is_admin or self.is_superuser
   
    def is_job_seeker(self):
        return self.role == self.Role.JOB_SEEKER.value

class UserLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs')
    last_login_date = models.DateTimeField(null=True)
    last_job_apply_date = models.DateTimeField(null=True)
    login_count = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True)
    
    def __str__(self):
        return f"Log for {self.user.email}"
    
class OrganisationRegister(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='organisation')
    org_name = models.CharField(max_length=255, verbose_name="Organization Name")
    org_description = models.TextField(null=True,blank=True)
    estd_date = models.DateField(verbose_name='Established Date')
    website_url = models.TextField(max_length=122,null=True,blank=True)
    logo = models.ImageField(upload_to='organisation_images/')
    
    def __str__(self):
        return self.org_name
    
class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    user_bio = models.TextField(blank=True,null=True,help_text="Tell Me About Yourself")
    current_designation = models.CharField(max_length=100, null=True, blank=True)
    experience_years = models.SmallIntegerField(default=0,help_text="default value will be 0")
    linkedin_url = models.URLField(blank=True,null=True)
    resume = models.FileField(upload_to='resumes/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class EducationDetails(models.Model):
    DEGREE_CHOICES = [
        ('PHD', 'Ph.D.'),
        ('MASTERS', 'Masters'),
        ('BACHELORS', 'Bachelors'),
        ('SENIOR', 'Senior'),
        ('SECONDARY', 'Secondary'),
        ('Other', 'Other'),
    ]
    
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name="education_detail")
    education_data = JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def add_education(self, education_info):
        """
        Add new education entry
        """
        if not isinstance(self.education_data, list):
            self.education_data = []
        
        # Validate the data structure based on degree type
        self.validate_education_data(education_info)
        
        # Add new education entry to the array
        self.education_data.append(education_info)
        self.save()

    def validate_education_data(self, data):
        """
        Validate education data based on degree type
        """
        required_fields = {
            'PHD': ['degree', 'institution', 'start_date', 'end_date', 'research_topic', 'thesis_title', 'supervisor'],
            'MASTERS': ['degree', 'institution', 'start_date', 'end_date', 'specialization', 'percentage'],
            'BACHELORS': ['degree', 'institution', 'start_date', 'end_date', 'major', 'percentage'],
            'SENIOR': ['degree', 'institution', 'start_date', 'end_date', 'board', 'percentage', 'stream'],
            'SECONDARY': ['degree', 'institution', 'start_date', 'end_date', 'board', 'percentage']
        }

        degree = data.get('degree')
        if degree not in dict(self.DEGREE_CHOICES):
            raise ValidationError(f"Invalid degree type: {degree}")

        # Check required fields
        if degree in required_fields:
            missing_fields = [field for field in required_fields[degree] if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields for {degree}: {', '.join(missing_fields)}")

        # Validate percentage if present
        if 'percentage' in data:
            try:
                percentage = float(data['percentage'])
                if not 0 <= percentage <= 100:
                    raise ValidationError("Percentage must be between 0 and 100")
            except (TypeError, ValueError):
                raise ValidationError("Invalid percentage value")

    def get_education_by_degree(self, degree):
        """
        Get all education entries of a specific degree type
        """
        return [edu for edu in self.education_data if edu.get('degree') == degree]

    def update_education(self, index, updated_data):
        """
        Update specific education entry by index
        """
        if 0 <= index < len(self.education_data):
            # Merge existing data with updates
            updated_entry = {**self.education_data[index], **updated_data}
            # Validate the merged data
            self.validate_education_data(updated_entry)
            self.education_data[index] = updated_entry
            self.save()
        else:
            raise IndexError("Education entry index out of range")

    def remove_education(self, index):
        """
        Remove education entry by index
        """
        if 0 <= index < len(self.education_data):
            self.education_data.pop(index)
            self.save()
        else:
            raise IndexError("Education entry index out of range")

    def __str__(self):
        return f"Education Details for {self.profile.user.username}"
    
class JobPosting(models.Model):
    JOB_TYPE_CHOICES = [
        ('FullTime', 'FullTime'),
        ('PartTime', 'PartTime'),
        ('ContractBased', 'ContractBased'),
        ('Intern', 'Intern'),
        ('FreeLancer', 'FreeLancer'),
    ]
    
    JOB_CATEGORY = [
        ('Teaching','Teaching'),
        ('NonTeaching','NonTeaching'),
        ('Administrative','Administrative'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_posting')
    organisation = models.ForeignKey(OrganisationRegister, on_delete=models.CASCADE, related_name='job_postings')
    job_type = models.CharField(max_length=25, choices=JOB_TYPE_CHOICES)
    job_category = models.CharField(max_length=25, choices=JOB_CATEGORY)
    job_title = models.CharField(max_length=120,help_text='Title for the job')
    job_description = models.TextField(help_text='description about required job')
    job_city = models.CharField(max_length=122,help_text='city of company')
    job_state = models.CharField(max_length=122,help_text='state of company')
    job_full_address = models.CharField(max_length=122,help_text='Full address of company')
    job_address_pin = models.CharField(max_length=110,help_text='pin number of the address')
    job_mobile = models.CharField(null=True,blank=True)
    job_email = models.EmailField(null=True,blank=True)
    job_is_remote = models.BooleanField(default=False)
    job_experience_required = models.SmallIntegerField(default=0)
    job_salary_offered = models.CharField(help_text='offered salary range')
    job_skills = models.TextField(help_text='skills required for the job')
    job_expiration_date = models.DateField(help_text='after this date job will be removed from the portal',null=True,blank=True)
    total_application = models.PositiveIntegerField(default=0, help_text="Total number of applications")
    # Job Status
    is_active = models.BooleanField(default=True, help_text="Is this job posting active?")
    is_featured = models.BooleanField(default=False, help_text="Is this job featured?")
    is_verified = models.BooleanField(default=False, help_text="Has this job been verified by admin?")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class JobApplication(models.Model):
    class ApplicationStatus(models.TextChoices):
        APPLIED = 'APPLIED', 'Applied'
        IN_REVIEW = 'IN_REVIEW', 'In Review'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        REJECTED = 'REJECTED', 'Rejected'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    job_seeker_profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE,related_name='applications')
    cover_letter = models.TextField(blank=True,null=True,help_text='optional cover letter provided by the applicant')
    resume = models.FileField(upload_to='job_applications/resumes/', blank=True, null=True, help_text="Optional resume upload; if not provided, the resume on the profile may be used.")
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.APPLIED,help_text="The current status of the application.")
    applied_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)
    employer_viewed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('job_posting', 'job_seeker_profile')
        ordering = ['-applied_at']
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        
    def __str__(self):
        return f"{self.job_seeker_profile.user.username} applied for {self.job_posting.job_title}"
            
    def save(self, *args, **kwargs):
        # Update job's application count when new application is created
        if not self.pk:  # Only on creation
            self.job_posting.total_application += 1
            self.job_posting.save()
        super().save(*args, **kwargs)    