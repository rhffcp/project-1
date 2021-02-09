from django.shortcuts import render

from . import util

from django import forms

class NewEntryTitle(forms.Form):
    entry_title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': "form-control"}))

class NewEntryContent(forms.Form):
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
            "contents": entry_page
        })

def search(request):
    search_value = request.GET.get('q','')
    entry_page = util.get_entry(search_value)
    entries = util.list_entries()

    suggestions = []
    for entry in entries:
        if search_value.upper() in entry.upper():
            suggestions.append(entry)

    if search_value in entries:
        return render(request, "encyclopedia/entry.html", {
            "entry_title": search_value,
            "contents": entry_page
    })
    else:
        return render(request, "encyclopedia/suggestions.html", {
            "suggestions": suggestions
        })

def new(request):
    if request.method == "POST":
        title = NewEntryTitle(request.POST)
        content = NewEntryContent(request.POST)

        if title.is_valid() and content.is_valid():
            entry_title = title.cleaned_data["entry_title"]
            entry_content = content.cleaned_data["entry_content"]

            if util.get_entry(entry_title) is None:
                util.save_entry(entry_title, entry_content)
                return render(request, "encyclopedia/entry.html", {
                    "entry_title": util.get_entry(entry_title),
                    "contents": util.get_entry(entry_content)
                })
            else:
                return render(request, "encyclopedia/error.html")


    return render(request, "encyclopedia/new.html", {
        "title": NewEntryTitle(),
        "content": NewEntryContent()
    })

