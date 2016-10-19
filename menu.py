import sublime
import sublime_plugin

from .menu_entry import MenuEntry
from .syntax_menu import build_syntax_menu


def get_super_menu():
    """Create a menu, which contains all menus."""
    if hasattr(get_super_menu, "super_menu"):
        return get_super_menu.super_menu
    menus = sublime.find_resources("*.sublime-menu")
    super_menu = MenuEntry("Super")
    for menu_path in menus:
        menu_id = menu_path.split("/")[-1].split(".")[0]
        res_str = sublime.load_resource(menu_path)
        mobj = sublime.decode_value(res_str)
        super_menu.add_child({
            "id": menu_id,
            "children": mobj
        })

    # manually create and add a syntax selection menu
    syntax_menu = build_syntax_menu()
    for i, child in enumerate(super_menu.children):
        if child.iden == "Syntax":
            super_menu.children[i] = syntax_menu
            break
    else:
        super_menu.children.append(syntax_menu)
    get_super_menu.super_menu = super_menu
    return super_menu


class show_in_panel():
    """Show a menu in a quickpanel."""

    def __init__(self, window, menu_entry, id_choices=None):
        self.window = window
        self.main = menu_entry
        if id_choices is not None:
            self._convert_choice_to_stack(id_choices)
        else:
            self.stack = self._retrieve_stack()
        self.show_quick_panel()

    def _convert_choice_to_stack(self, id_choices):
        entry = self.main
        self.stack = []
        for id_choice in id_choices:
            for i, child in enumerate(entry.children):
                if child.iden == id_choice or child.caption == id_choice:
                    self.stack.append(i)
                    entry = child
                    break
            else:
                # did not break => choice not found
                print("Not found choice {0}".format(id_choice))
                return

    def _retrieve_stack(self):
        return self.window.settings().get("mp_choice_stack", [])

    def _store_stack(self):
        self.window.settings().set("mp_choice_stack", self.stack)

    def show_quick_panel(self):
        entry = self.main
        index = -1
        for i in self.stack:
            try:
                child = entry.children[i]
            except:
                break
            if not child.is_leaf():
                entry = child
            elif not child.is_command():
                entry = child
                break
            else:
                index = i
                self.stack.pop()
                break
        self.entry = entry
        self.entries = ["{0}".format(e.caption) if e.is_command()
                        else "[{0}]".format(e.caption)
                        for e in entry.children]

        # insert an option to go upwards on the stack
        if self.stack:
            self.entries.insert(0, "..")
            if index != -1:
                index += 1
        self.window.show_quick_panel(self.entries,
                                     self.select_item,
                                     on_highlight=lambda x: None,
                                     selected_index=index,
                                     flags=sublime.KEEP_OPEN_ON_FOCUS_LOST)

    def select_item(self, index):
        if index == -1:
            self._store_stack()
            return
        elif self.stack:
            if index == 0:
                self.stack.pop()
                self.show_quick_panel()
                return
            index -= 1
        self.stack.append(index)
        child = self.entry.children[index]
        if child.is_leaf() and child.is_command():
            self._store_stack()
            print("Run Command:", child.command)
            if child.command:
                self.window.run_command(**child.command)
        else:
            self.show_quick_panel()


def update_tab_ctx(window, super_menu):
    try:
        tab_menu = super_menu.get_child("Tab Context")
    except:
        print("No Tab context available")
        return

    view = window.active_view()

    group, index = window.get_view_index(view)

    for child in tab_menu.children:
        args = child.command.get("args")
        if not args:
            continue
        if "index" in args:
            args["index"] = index
        if "group" in args:
            args["group"] = group


def update_sidebar_ctx(window, super_menu):
    try:
        sidebar_menu = super_menu.get_child("Side Bar")
    except:
        print("No SideBar context available")
        return

    view = window.active_view()

    group, index = window.get_view_index(view)
    path = view.file_name()

    for child in sidebar_menu.children:
        if child.caption.startswith("Ne"):
            print(child.iden, child.caption)
        if not child.command:
            continue
        args = child.command.get("args")
        if not args:
            continue
        if "paths" in args and args["paths"] == []:
            args["paths"] = [path]


class MenuNavigatorShowMenuCommand(sublime_plugin.WindowCommand):
    def run(self, id_choices=None):
        super_menu = get_super_menu()
        update_tab_ctx(self.window, super_menu)
        update_sidebar_ctx(self.window, super_menu)
        show_in_panel(self.window, super_menu, id_choices)


def plugin_loaded():
    """Cache the menu creation in the background"""
    sublime.set_timeout_async(get_super_menu, 5000)
