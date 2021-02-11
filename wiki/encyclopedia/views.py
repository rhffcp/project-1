from django.shortcuts import render
from . import util
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
import random
import markdown2
from markdown2 import Markdown

markdowner = Markdown()

class NewEntryForm(forms.Form):
    entry_title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': "form-control"}))
    entry_content = forms.CharField(label="Content", widget=forms.Textarea(attrs={'class': "form-control", 'style': "height: 200px"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    entry_page = util.get_entry(entry)
    if entry_page is None:
        return render(request, "encyclopedia/error.html", {
            "entry_title": entry,
            "error": True
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry_title": entry,
            "contents": markdowner.convert(entry_page) 
        })

def search(request):
    search_value = request.GET.get('q','')
    entries = util.list_entries()

    suggestions = []
    for entry in entries:
        if search_value.upper() in entry.upper():
            suggestions.append(entry)

    if search_value in entries:
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': search_value}))

    else:
        return render(request, "encyclopedia/suggestions.html", {
            "suggestions": suggestions
        })

def new(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)

        if form.is_valid():
            entry_title = form.cleaned_data["entry_title"]
            entry_content = form.cleaned_data["entry_content"]

            if util.get_entry(entry_title) is None:
                util.save_entry(entry_title, entry_content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': entry_title}))
            else:
                return render(request, "encyclopedia/new.html", {
                    "exists": True,
                    "entry_title": entry_title,
                    "form": NewEntryForm()
                })


    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm()
    })

def edit(request, entry):
    form = NewEntryForm()
    entry_page = util.get_entry(entry)
    
    form.fields["entry_title"].initial = entry
    form.fields["entry_content"].initial = entry_page
    form.fields["entry_title"].widget = forms.HiddenInput()

    return render(request, "encyclopedia/edit.html", {
        "entry_title": entry,
        "form": form
    })

def update(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)

        if form.is_valid():
            entry_title = form.cleaned_data["entry_title"]
            entry_content = form.cleaned_data["entry_content"]

            if util.get_entry(entry_title):
                util.save_entry(entry_title, entry_content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': entry_title}))

def random_entry(request):
    random_entry = random.choice(util.list_entries())

    return HttpResponseRedirect(reverse("entry", kwargs={'entry': random_entry}))