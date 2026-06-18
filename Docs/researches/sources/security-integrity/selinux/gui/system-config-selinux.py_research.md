# sources/security-integrity/selinux/gui/system-config-selinux.py

## Purpose
`system-config-selinux.py` is the main GTK application for graphical SELinux administration. It loads the UI definition, constructs the navigation list and notebook pages, and dispatches menu/toolbar actions to the currently selected page object.

## Important APIs, types, and functions
The main class is `childWindow`. Its constructor connects builder signals, adds `statusPage`, and, when SELinux is enabled, adds booleans, file contexts, logins, users, ports, modules, and domains pages. `add_page()` appends page objects. `setupScreen()` builds the left navigation `Gtk.ListStore` from each page's `get_description()`. `itemSelected()` keeps the hidden notebook page and menu sensitivity synchronized. `add()`, `delete()`, `properties()`, and `on_local_clicked()` delegate to the active tab. `policy()` and `logging()` spawn external tools.

## Control flow
Import-time setup requires GTK 3, handles missing DISPLAY-related runtime errors, appends `/usr/share/system-config-selinux`, imports page modules, initializes gettext, and loads `system-config-selinux.ui`. Standalone execution resets SIGINT, constructs `childWindow`, calls `stand_alone()`, builds screen state, shows the main window, and enters `Gtk.main()`. The left-side tree selection drives which page is visible and whether edit menus are enabled.

## State and persistence behavior
Application state is in `self.tabs`, selected navigation rows, the hidden notebook index, menu sensitivity, and page-local state. The main shell does not directly persist SELinux data; page objects perform those changes through libselinux bindings, `semanage`, or other helpers.

## Dependencies and integration points
The script depends on PyGObject GTK 3, the Python SELinux bindings, peer page modules, the installed UI XML, gettext domain `selinux-gui`, `semanagegui.py`, and `seaudit`. It is launched through the privileged shell wrapper and referenced by the desktop entry.

## Risks and edge cases
The script uses fixed installed paths, so development-tree execution without installed assets fails. Some exception handling uses `e.message`, which is not portable to Python 3. `os.spawnl()` calls do not pass an explicit argv[0], which can be fragile depending on platform behavior. If SELinux is disabled, only the status page is added; menu dispatch must therefore respect `use_menus(False)` on that page.

## Test signals
Tests should mock GTK builder objects and page classes to verify tab construction with SELinux enabled/disabled, selection-to-notebook synchronization, menu sensitivity, action delegation to active tabs, no-DISPLAY error behavior, and external tool spawn calls.
