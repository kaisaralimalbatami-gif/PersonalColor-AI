from django import forms


class KirimHasilForm(forms.Form):
    nama = forms.CharField(
        label="Nama Anda", max_length=50,
        error_messages={"required": "Nama wajib diisi.", "max_length": "Nama maksimal 50 karakter."},
        widget=forms.TextInput(attrs={"placeholder": "Masukkan nama Anda", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="Alamat Email",
        error_messages={"required": "Email wajib diisi.", "invalid": "Alamat email tidak valid."},
        widget=forms.EmailInput(attrs={"placeholder": "nama@email.com", "autocomplete": "email"}),
    )
