import datetime
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .constant import NUM_OF_WEEKS
from catalog.models import BookInstance


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text=_("Enter a date between now and 4 weeks" "(default 3).")
    )

    def clean_renewal_date(self):
        data = self.cleaned_data["renewal_date"]
        if data < datetime.date.today():
            raise ValidationError(_("Invalid date - renewal in past"))
        if data > datetime.date.today() + datetime.timedelta(weeks=NUM_OF_WEEKS):
            raise ValidationError(
                _(f"Invalid date - renewal more than {NUM_OF_WEEKS} weeks")
            )
        return data


class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data["due_back"]
        if data < datetime.date.today():
            raise ValidationError(_("Invalid date - renewal in past"))
        if data > datetime.date.today() + datetime.timedelta(weeks=NUM_OF_WEEKS):
            raise ValidationError(
                _(f"Invalid date - renewal more than {NUM_OF_WEEKS} weeks")
            )
        return data

    class Meta:
        model = BookInstance
        fields = ["due_back"]
        labels = {"due_back": _("Renewal date")}
        help_texts = {
            "due_back": _(
                f"Enter a date between now and {NUM_OF_WEEKS} weeks (default 3). "
            )
        }
        