from django.shortcuts import render

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    entry_page = util.get_entry(entry)
    if entry_page is None:
        return render(request, "encyclopedia/error.html", {
            "entry_title": entry
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

