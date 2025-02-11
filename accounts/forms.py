import json
from django import forms
from .models import *
from django.forms import inlineformset_factory, modelformset_factory


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}), required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}), required=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name','role', 'phone_number', 'dob', 'gender','user_image',]
        
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'user_image': forms.FileInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if not password or not confirm_password:
            raise forms.ValidationError("Password and Confirm Password fields are required.")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        # Additional validation for username
        username = cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")

        return cleaned_data
    
class OrganisationRegistrationForm(forms.ModelForm):
    class Meta:
        model = OrganisationRegister
        fields = ['org_name', 'org_description', 'estd_date', 'website_url', 'logo']
        widgets = {
            'estd_date': forms.DateInput(attrs={'type': 'date'}),
            'org_description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your organization...'}),
            'website_url': forms.URLInput(attrs={'placeholder': 'https://'}),
        }
        
class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['user_bio', 'current_designation', 'experience_years', 'linkedin_url', 'resume']
        widgets = {
            'user_bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell Us About Yourself'}),
            'linkedin_url': forms.URLInput(attrs={'placeholder': 'https://'}),
            'resume': forms.FileInput(),
        }
        
            
class EducationEntryForm(forms.Form):
    DEGREE_CHOICES = EducationDetails.DEGREE_CHOICES
    
    degree = forms.ChoiceField(choices=DEGREE_CHOICES)
    institution = forms.CharField(max_length=200)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    # Common optional fields
    percentage = forms.FloatField(required=False, min_value=0, max_value=100)
    board = forms.CharField(required=False, max_length=100)
    
    # Degree-specific fields
    research_topic = forms.CharField(required=False, max_length=200)
    thesis_title = forms.CharField(required=False, max_length=200)
    supervisor = forms.CharField(required=False, max_length=100)
    specialization = forms.CharField(required=False, max_length=100)
    major = forms.CharField(required=False, max_length=100)
    stream = forms.CharField(required=False, max_length=100)

    def clean(self):
        cleaned_data = super().clean()
        degree = cleaned_data.get('degree')
        
        # Define required fields for each degree type
        required_fields = {
            'PHD': ['research_topic', 'thesis_title', 'supervisor'],
            'MASTERS': ['specialization', 'percentage'],
            'BACHELORS': ['major', 'percentage'],
            'SENIOR': ['board', 'percentage', 'stream'],
            'SECONDARY': ['board', 'percentage'],
        }
        
        if degree in required_fields:
            for field in required_fields[degree]:
                if not cleaned_data.get(field):
                    self.add_error(field, 'This field is required for selected degree')

        return cleaned_data

EducationFormSet = forms.formset_factory(
    EducationEntryForm,
    extra=1,
    max_num=5,
    validate_max=True,
    min_num=1,
    validate_min=True
)

class UserForm(forms.ModelForm):
    """Form for updating user details except password"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number','address', 'dob', 'gender', 'user_image']
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
        }

class EducationDetailsForm(forms.ModelForm):
    """Form for updating education details"""
    class Meta:
        model = EducationDetails
        fields = ["education_data"]

    def clean_education_data(self):
        """Ensure valid JSON structure"""
        data = self.cleaned_data.get("education_data")
        if isinstance(data, str):
            try:
                return json.loads(data)  # Convert JSON string to dict
            except json.JSONDecodeError:
                raise forms.ValidationError("Invalid education data format.")
        return data

# Formset for multiple education entries
EducationDetailsFormSet = modelformset_factory(EducationDetails, form=EducationDetailsForm, extra=1, can_delete=True)

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            'job_title', 'job_description', 'job_category', 'job_type', 'job_city',
            'job_state', 'job_full_address', 'job_address_pin', 'job_mobile',
            'job_email', 'job_is_remote', 'job_experience_required', 'job_salary_offered',
            'job_skills', 'is_active','is_verified','job_expiration_date'
        ]
        
        widgets = {
            'job_description': forms.Textarea(attrs={'rows': 4}),
            'job_skills': forms.Textarea(attrs={'rows': 2}),
            'job_salary_offered': forms.TextInput(attrs={'placeholder': 'e.g. 30,000-50,000 INR'}),
            'job_mobile': forms.TextInput(attrs={'placeholder': 'e.g. +91 9876543210'}),
            'job_expiration_date':forms.DateInput(attrs={"type": "date"})
        }
        

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'resume']