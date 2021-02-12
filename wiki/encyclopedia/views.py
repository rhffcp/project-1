import random

from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from . import util

# Import Markdown class from markdown2 module (for md to html conversion)
from markdown2 import Markdown

# Instantiating Markdown class.
markdowner = Markdown()


# New entry form class which inherits the Form class from forms module.
class NewEntryForm(forms.Form):
    # Title form.
    entry_title = forms.CharField(
        label="Title", widget=forms.TextInput(attrs={'class': "form-control"}))
    # Content form.
    entry_content = forms.CharField(label="Content", widget=forms.Textarea(
        attrs={'class': "form-control", 'style': "height: 200px"}))


# The request object contains info about the user's request like get or post methods.

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

    # If contents for entry doesn't exist,
    # render the error page.
    if contents is None:
        return render(request, "encyclopedia/error.html", {
            "entry_title": entry,
            "error": True
        })
    # Otherwise, redirect to entry page.
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry_title": entry,
            # Uses the convert method from Markdown class to convert md to html.
            "contents": markdowner.convert(contents) 
        })


def search(request):
    """
    Search for an entry: if query exists, redirect to that page
    otherwise, show suggestions for unmatched queries.
    """
    # Get the value of a GET variable with the name q 
    # that returns nothing if it doesn't exist, and save it to search_value.
    search_value = request.GET.get('q', '')
    entries = util.list_entries()

    # If a substring from a query is inside an entry, add that entry to suggestions list.
    suggestions = []
    for entry in entries:
        if search_value.upper() in entry.upper():
            suggestions.append(entry)

    # If query already exists as an entry, redirect to that entry page via "entry" path.
    if search_value in entries:
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': search_value}))
    # Otherwise, render the suggestions page with suggestions list as context.
    else:
        return render(request, "encyclopedia/suggestions.html", {
            "suggestions": suggestions
        })


def new(request):
    """
    Create new entry: if entry exists, give an alert
    otherwise, save and redirect to new entry.
    """
    # If method is post
    if request.method == "POST":
        # take the data user submitted (in both title and content) and save it inside form.
        form = NewEntryForm(request.POST)

        # If form is valid on server side
        # clean up (properly format) the data inside the form fields and save them to variables. 
        if form.is_valid():
            entry_title = form.cleaned_data["entry_title"]
            entry_content = form.cleaned_data["entry_content"]

            # If title data doesn't exist, save the title data and content data as a new entry
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
    Edit an entry: displays pre-populated content which can be altered.
    """
    form = NewEntryForm()
    contents = util.get_entry(entry)

    # Specify initial values for for particular fields.
    form.fields["entry_title"].initial = entry
    form.fields["entry_content"].initial = contents
    # Hides the title field.
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
        # take the data user submitted (in both title and content) and save it inside form.
        form = NewEntryForm(request.POST)

        # If form is valid on server side
        # clean up (properly format) the data inside the form fields and save them to variables. 
        if form.is_valid():
            entry_title = form.cleaned_data["entry_title"]
            entry_content = form.cleaned_data["entry_content"]

            # If title data exists, update the title data and content data 
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
