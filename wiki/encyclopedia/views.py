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