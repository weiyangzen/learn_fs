# sources/security-integrity/selinux/gui/usersPage.py

## Purpose
`usersPage.py` implements the "SELinux User" management page for the GUI. It lists SELinux users, MLS/MCS ranges, and roles, and supports add, modify, and delete operations through `semanage user`.

## Important APIs, types, and functions
`usersPage` extends `semanagePage`. Its constructor creates a `Gtk.ListStore`, adds columns for user, range, and roles, loads existing data from `seobject.seluserRecords().get_all()`, and binds dialog entries. `load()` filters and displays translated ranges via `seobject.translate()`. `dialogInit()` and `dialogClear()` move data between selected rows and the dialog. `add()`, `modify()`, and `delete()` shell out to `semanage user`.

## Control flow
The page is constructed by the main application when SELinux is enabled. It loads current records immediately. Menu or toolbar actions call base dialog wrappers, which call page-specific add/modify/delete methods. Successful add appends a row; successful modify reloads the page; successful delete removes the selected row after preventing deletion of required users.

## State and persistence behavior
Display state is in the GTK model, selected rows, filter text, and dialog entries. Persistent state is modified by `semanage user -a`, `-m`, and `-d`, which update SELinux user definitions in local policy. The page does not maintain its own on-disk data.

## Dependencies and integration points
The module depends on GTK/GObject, `seobject`, the `semanage` CLI, gettext, and the common `semanagePage` base. It relies on widget IDs from `system-config-selinux.ui` and is listed in the main navigation by `system-config-selinux.py`.

## Risks and edge cases
User, range, and roles are interpolated into shell commands. Roles are single-quoted, but embedded quotes can still be problematic, and user/range are unquoted. Only `root` and `user_u` are protected from deletion. The `range` variable shadows the built-in, which is harmless locally but reduces readability. Errors from `semanage` are surfaced as text but not parsed.

## Test signals
Tests should mock `seobject.seluserRecords`, `seobject.translate`, and `getstatusoutput()` to cover filtering, add/modify/delete command generation, required-user delete protection, list reload after modify, store append/remove behavior, and handling of command failures.
