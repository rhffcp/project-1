import random

from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from . import util

from markdown2 import Markdown

markdowner = Markdown()


class NewEntryForm(forms.Form):
    # Title form.
    entry_title = forms.CharField(
        label="Title", widget=forms.TextInput(attrs={'class': "form-control"}))
    # Content form.
    entry_content = forms.CharField(
        label="Content", widget=forms.Textarea(attrs={'class': "form-control", 'style': "height: 200px"}))


# **The request object contains info about the user's request like get or post methods.**

def index(request):
    """
    Home page view: lists all entries.
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry):
    """
    Entry page view: displays the title and contents of an entry.
    """
    contents = util.get_entry(entry)

    # If contents for entry does not exist,
    # render the error page.
    if contents is None:
        return render(request, "encyclopedia/error.html", {
            "entry_title": entry,
        })
    # Otherwise, redirect user to entry page.
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry_title": entry,
            # Convert md to html.
            "contents": markdowner.convert(contents) 
        })


def search(request):
    """
    Search for an entry: if query already exists, redirect user to that page,
    otherwise, display suggestions.
    """
    # Get the value of a GET variable with the name q 
    # and return nothing if value does not exist.
    search_value = request.GET.get('q', '')
    entries = util.list_entries()

    # If a substring from a query is part of an existing entry, add that entry to suggestions list.
    suggestions = []
    for entry in entries:
        if search_value.upper() in entry.upper():
            suggestions.append(entry)

    # If query already exists, redirect user to that entry page.
    if search_value in entries:
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': search_value}))
    # Otherwise, render the suggestions page.
    else:
        return render(request, "encyclopedia/suggestions.html", {
            "suggestions": suggestions
        })


def new(request):
    """
    Create new entry: if entry exists, give an alert,
    otherwise, save and redirect user to new entry.
    """
    # If method is post
    if request.method == "POST":
        # get user submitted data.
        form = NewEntryForm(request.POST)

        # If form is valid on server side
        # format data inside the form fields and save them to variables. 
        if form.is_valid():
            entry_title = form.cleaned_data["entry_title"]
            entry_content = form.cleaned_data["entry_content"]

            # If title data does not exist, save title and content as a new entry
            # and redirect user to that entry page.
            if util.get_entry(entry_title) is None:
                util.save_entry(entry_title, entry_content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': entry_title}))
            # Otherwise, re-render the page and give an alert.
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
    """
    Edit an entry: displays pre-populated content which can be edited.
    """
    form = NewEntryForm()
    contents = util.get_entry(entry)

    # Specify initial values for for particular fields.
    form.fields["entry_title"].initial = entry
    form.fields["entry_content"].initial = contents
    # Hide title field.
    form.fields["entry_title"].widget = forms.HiddenInput()

    return render(request, "encyclopedia/edit.html", {
        "entry_title": entry,
        "form": form
    })


def update(request):
    """
    Update edit: replaces and saves edited entry.
    """
    # If method is post
    if request.method == "POST":
        # get user submitted data.
        form = NewEntryForm(request.POST)

        # If form is valid on server side
        # format data inside the form fields and save them to variables. 
        if form.is_valid():
            entry_title = form.cleaned_data["entry_title"]
            entry_content = form.cleaned_data["entry_content"]

            # If title data exists, update the content 
            # and redirect user to that entry page.
            if util.get_entry(entry_title):
                util.save_entry(entry_title, entry_content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': entry_title}))


def random_entry(request):
    """
    Display a random entry.
    """
    random_entry = random.choice(util.list_entries())

    return HttpResponseRedirect(reverse("entry", kwargs={'entry': random_entry}))
