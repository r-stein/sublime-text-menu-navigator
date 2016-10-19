import re


_RE_PLACEHOLDER_COMMAND = re.compile(r"^\$\w+")


def get_caption(entry_dict):
    caption = entry_dict.get("caption", entry_dict.get("id", None))
    if caption:
        return caption
    caption = entry_dict["command"]
    if _RE_PLACEHOLDER_COMMAND.match(caption):
        return "-"
    caption = re.sub(r'_(\w)', lambda m: m.expand(r' \1').upper(), caption)
    caption = caption[0].upper() + caption[1:]
    return caption


def get_id(entry_dict):
    caption = entry_dict.get(
        "id", entry_dict.get("caption", entry_dict.get("command")))
    return caption


class ChildMissingException(Exception):
    pass


class MenuEntry():
    def __init__(self, caption, iden=None, command=None):
        self.iden = iden or caption
        self.caption = caption
        self.children = []
        self._child_map = {}
        self.command = command

    def get_child(self, *names):
        for caption in names:
            caption = caption.lower()
            if caption in self._child_map:
                return self._child_map[caption]
        raise ChildMissingException(", ".join(names))

    def _insert_child(self, child):
        self._child_map[child.iden.lower()] = child
        self._child_map[child.caption.lower()] = child
        self.children.append(child)

    def add_children(self, children_array):
        for child_dict in children_array:
            self.add_child(child_dict)

    def add_child(self, child_dict):
        caption = get_caption(child_dict)
        name = caption
        if name == "-":
            return
        iden = get_id(child_dict)
        # TODO??? just use caption?
        # iden = caption
        # add the child to the children
        try:
            child = self.get_child(caption, iden)
        except:
            command = None
            if "command" in child_dict:
                command = {
                    "cmd": child_dict["command"],
                    "args": child_dict.get("args", None)
                }
            child = MenuEntry(name, iden, command=command)
            # self._child_map[iden] = child
            self._insert_child(child)
            # self.children.append(child)
        # if iden not in self._child_map:
        #     command = None
        #     if "command" in child_dict:
        #         command = {
        #             "cmd": child_dict["command"],
        #             "args": child_dict.get("args", None)
        #         }
        #     child = MenuEntry(name, iden, command=command)
        #     self._child_map[iden] = child
        #     self.children.append(child)
        # else:
        #     child = self._child_map[iden]

        # if we have grandchildren, add those to the child
        if "children" not in child_dict:
            return

        grandchildren = child_dict["children"] or []
        child.add_children(grandchildren)

    def is_leaf(self):
        return not bool(self.children)

    def is_command(self):
        return bool(self.command)

    def __repr__(self):
        if self.is_leaf():
            return self.caption
        child_str = ", ".join(map(repr, self.children))
        return "{{{0}: [{1}]}}".format(self.caption, child_str)
