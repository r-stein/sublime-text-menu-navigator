import collections
import sublime

from .menu_entry import MenuEntry


def _create_file_entry(name, path):
    entry = MenuEntry(name)
    entry.command = {
        "command": "set_file_type",
        "args": {"syntax": path}
    }


def build_syntax_menu():
    """Create the syntax menu."""
    tm_syntax_files = sublime.find_resources("*.tmLanguage")
    syntax_files = sublime.find_resources("*.sublime-syntax")
    tm_syntax_files = [
        s for s in tm_syntax_files
        if s.replace(".tmLanguage", ".sublime-syntax")
        not in syntax_files
    ]

    syntax_files.extend(tm_syntax_files)
    syn_dict = collections.OrderedDict({})
    for syntax_file in syntax_files:
        split = syntax_file.split("/")
        package = split[1]
        file = split[-1].split(".")[0]
        if package in syn_dict:
            syn_dict[package].append((file, syntax_file))
        else:
            syn_dict[package] = [(file, syntax_file)]

    syntax_menu = MenuEntry("Syntax")

    sorted_dict = sorted(syn_dict.items(), key=lambda i: i[0].lower())
    od = collections.OrderedDict(sorted_dict)
    for package, file_infos in od.items():
        if len(file_infos) == 1:
            file, path = file_infos[0]
            entry = _create_file_entry(file, path)
        else:
            entry = MenuEntry(package)
            for file, path in file_infos:
                child = _create_file_entry(file, path)
                entry.children.append(child)
        syntax_menu.children.append(entry)

    return syntax_menu
