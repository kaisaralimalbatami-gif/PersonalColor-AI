from django.shortcuts import render


def opsi(request):
    return render(request, "analisis/opsi.html")