
from django import forms
from django.contrib.auth import get_user_model
from employees.models import Employee

from businesses.models import Business, BusinessMembership


User = get_user_model()


class BusinessRegistrationForm(forms.Form):
    # ============================================================
    # BUSINESS INFORMATION
    # ============================================================

    business_name = forms.CharField(
        max_length=200,
        label="Business Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. Lisa's Beauty Salon",
            }
        ),
    )

    business_type = forms.ChoiceField(
        choices=Business.BusinessType.choices,
        label="Business Type",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    business_email = forms.EmailField(
        label="Business Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "business@example.com",
            }
        ),
    )

    business_phone = forms.CharField(
        max_length=30,
        label="Business Phone",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. 060 000 0000",
            }
        ),
    )

    address = forms.CharField(
        label="Business Address",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Business address",
            }
        ),
    )

    city = forms.CharField(
        max_length=100,
        label="City",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "City",
            }
        ),
    )

    province = forms.CharField(
        max_length=100,
        label="Province",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Province",
            }
        ),
    )

    # ============================================================
    # BUSINESS OWNER INFORMATION
    # ============================================================

    first_name = forms.CharField(
        max_length=150,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )

    email = forms.EmailField(
        label="Owner Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
            }
        ),
    )

    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Choose a username",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a password",
            }
        ),
    )

    password_confirmation = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm your password",
            }
        ),
    )

    # ============================================================
    # VALIDATION
    # ============================================================

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_business_email(self):
        return self.cleaned_data["business_email"].strip().lower()

    def clean_business_phone(self):
        return self.cleaned_data["business_phone"].strip()

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get(
            "password_confirmation"
        )

        if password and password_confirmation:
            if password != password_confirmation:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data

    # ============================================================
    # CREATE USER + BUSINESS + MEMBERSHIP
    # ============================================================

    def save(self):
        """
        Creates:
        1. Business owner User
        2. Business
        3. BusinessMembership linking the owner to the business
        """

        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            role=User.PlatformRole.USER,
        )

        business = Business.objects.create(
            name=self.cleaned_data["business_name"],
            business_type=self.cleaned_data["business_type"],
            owner=user,
            email=self.cleaned_data["business_email"],
            phone=self.cleaned_data["business_phone"],
            address=self.cleaned_data["address"],
            city=self.cleaned_data["city"],
            province=self.cleaned_data["province"],
        )

        BusinessMembership.objects.create(
            business=business,
            user=user,
            role=BusinessMembership.Role.OWNER,
        )

        return user, business


class StaffCreationForm(forms.Form):
    # ============================================================
    # STAFF INFORMATION
    # ============================================================

    first_name = forms.CharField(
        max_length=150,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "staff@example.com",
            }
        ),
    )

    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
            }
        ),
    )

    role = forms.ChoiceField(
        label="Staff Role",
        choices=[
            (
                BusinessMembership.Role.MANAGER,
                "Manager",
            ),
            (
                BusinessMembership.Role.RECEPTIONIST,
                "Receptionist",
            ),
            (
                BusinessMembership.Role.BARBER,
                "Barber",
            ),
            (
                BusinessMembership.Role.STYLIST,
                "Stylist",
            ),
            (
                BusinessMembership.Role.ACCOUNTANT,
                "Accountant",
            ),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    password = forms.CharField(
        label="Temporary Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Temporary password",
            }
        ),
    )

    password_confirmation = forms.CharField(
        label="Confirm Temporary Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
            }
        ),
    )

    # ============================================================
    # VALIDATION
    # ============================================================

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get(
            "password_confirmation"
        )

        if password and password_confirmation:
            if password != password_confirmation:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data

    # ============================================================
    # CREATE STAFF USER + MEMBERSHIP
    # ============================================================


    def save(self, business):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            role=User.PlatformRole.USER,
        )

        membership = BusinessMembership.objects.create(
            business=business,
            user=user,
            role=self.cleaned_data["role"],
        )

        Employee.objects.create(
            user=user,
            business=business,
            membership=membership,
            position=self.cleaned_data["role"],
        )

        return user, membership


class CustomerRegistrationForm(forms.Form):
    # ============================================================
    # CUSTOMER INFORMATION
    # ============================================================

    first_name = forms.CharField(
        max_length=100,
        label="First Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=100,
        label="Last Name",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )

    phone = forms.CharField(
        max_length=30,
        label="Phone Number",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "e.g. 060 123 4567",
            }
        ),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
            }
        ),
    )

    username = forms.CharField(
        max_length=150,
        label="Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Choose a username",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Create a password",
            }
        ),
    )

    password_confirmation = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm your password",
            }
        ),
    )

    # ============================================================
    # VALIDATION
    # ============================================================

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        if User.objects.filter(
            username__iexact=username
        ).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        if not phone:
            raise forms.ValidationError(
                "Phone number is required."
            )

        return phone

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get(
            "password_confirmation"
        )

        if password and password_confirmation:

            if password != password_confirmation:

                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data

    # ============================================================
    # CREATE CUSTOMER USER + CUSTOMER PROFILE
    # ============================================================

    def save(self, business):
        from customers.models import Customer

        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        customer = Customer.objects.create(
            business=business,
            user=user,
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            phone=self.cleaned_data["phone"],
            email=self.cleaned_data["email"],
            is_active=True,
        )

        return user, customer
