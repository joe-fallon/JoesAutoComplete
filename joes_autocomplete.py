import sublime_plugin
import sublime
import re
import time

MIN_WORD_SIZE = 3
MAX_WORD_SIZE = 50
MAX_VIEWS = 1000

class JoesAutocomplete(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        words = []
        current_view_words = []
        view_words = []
        

        # Limit number of views but always include the active view. This
        # view goes first to prioritize matches close to cursor position.
        other_views = [v for v in sublime.active_window().views() if v.id() != view.id()]
        views = [view] + other_views
        views = views[0:MAX_VIEWS]
        
        for v in views:
            if len(locations) > 0 and v.id() == view.id():
                current_view_words = extract_completions(v, prefix, locations[0])
            else:
                view_words = extract_completions(v, prefix)

            if len(view_words) == 0:
                view_words = all_words(v)

            words += view_words
            view_words = []

        # The method extract_completions will return an empty list if an empty prefix
        # is passed in. This fixes that behavior.
        if len(current_view_words) == 0:
            current_view_words = all_words(view)

        current_view_words = filter_words(current_view_words, prefix)
        words = filter_words(words, prefix)   
        # words = sorted(words, key=lambda s: s.lower())

        # Prioritize the current view's words to the top.
        words = current_view_words + words
        words = without_duplicates(words)
        words = sorted(words, key=lambda s: s.lower())

        # Convert list to tuples.
        words = [(w, w.replace('$', '\\$')) for w in words]

        # Override the default words completions due to our list being much better.
        # return (words, sublime.INHIBIT_WORD_COMPLETIONS)
        return words

def extract_completions(view, prefix, location=None):
    words = []
    if location != None:
        words += view.extract_completions(prefix.upper(), location)
        words += view.extract_completions(prefix.lower(), location)
    else:
        words += view.extract_completions(prefix.upper())
        words += view.extract_completions(prefix.lower())
    return words

def all_words(view):
    tokens = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    tokens += [chr(i) for i in range(ord('0'), ord('9') + 1)]
    tokens += ["_"]
    words = []
    for t in tokens:
        words += extract_completions(view, t)
    return words

def filter_words(words, prefix=None):
    words = [w for w in words if MIN_WORD_SIZE <= len(w) <= MAX_WORD_SIZE]
    # print words

    results = []
    for w in words:
        if prefix == None or prefix != w:
            results.append(w)
    return results

def without_duplicates(words):
    result = []
    for w in words:
        if w not in result:
            result.append(w)
    return result
