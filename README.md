# MenuNavigator

The MenuNavigator enables a keyboard driven access to the menus, which are usually mouse driven.
This is done via a quick panel.


## Issues

Since there is no API to access the actual menu, this package scans all `*.sublime-menu` and tries to mimic the behavior of the actual menu. Therefore some entries might be missing and some commands might not work.

__Known issues__:

- The *Open Recent*-menu is always empty.
- Some Context-Menu entries require an event and raise an error
- The SideBar-Menu is not working correct

## Demonstration

