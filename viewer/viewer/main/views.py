from django.shortcuts import render
from os import path

# Create your views here.

def main(request):
    return render(request, 'index.html')

def read_default(request):
    mytree = open(path.abspath('./../../mytree.json'), 'r').read()
    labels = open(path.abspath('./../../labels.json'), 'r').read()
    return render(request, 'default_input.html', {
        'tree': mytree,
        'labels': labels,
    })