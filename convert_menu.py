import re
import json

import sublime

from .menu_entry import MenuEntry
from .syntax_menu import build_syntax


def json_compatibility(s):
    # remove comment lines
    # we remove the whole line, because otherwise we might miss some escapes
    # e.g. comment inside strings etc
    s = re.sub(r".*(?!:)//.*", "", s)
    # remove , before json endings
    s = re.sub(r"(.)\s*\,[\s\n]*([\}\]])", r"\1\2", s, flags=re.MULTILINE)
    # double escape escapes
    s = s.replace("\\", "\\\\")
    # single escape strings again
    s = s.replace("\\\\\"", "\\\"")
    return s


def get_super_menu():
    """Create a menu, which contains all menus."""
    if hasattr(get_super_menu, "super_menu"):
        return get_super_menu.super_menu
    menus = sublime.find_resources("*.sublime-menu")
    super_menu = MenuEntry("Super")
    for menu_path in menus:
        menu_id = menu_path.split("/")[-1].split(".")[0]
        res_str = sublime.load_resource(menu_path)
        res_comp = json_compatibility(res_str)
        try:
            mobj = json.loads(res_comp)
        except:
            print("Failed to load menu for {0}".format(menu_id))
            continue
        super_menu.add_child({
            "id": menu_id,
            "children": mobj
        })

    # manually create and add a syntax selection menu
    syntax_menu = build_syntax()
    for i, child in enumerate(super_menu.children):
        if child.iden == "Syntax":
            super_menu.children[i] = syntax_menu
            break
    else:
        super_menu.children.append(syntax_menu)
    get_super_menu.super_menu = super_menu
    return super_menu
