# sources/security-integrity/selinux/gui/semanagePage.py

## Purpose
`semanagePage.py` defines the common base class for SELinux GUI pages that manage semanage-backed records. It centralizes filter handling, row activation, confirmation dialogs, add/modify dialog loops, delete confirmation, local/customized toggling, search behavior, and busy cursor state.

## Important APIs, types, and functions
`idle_func()` drains pending GTK events so cursor changes become visible during blocking operations. `semanagePage.__init__()` binds common widgets named from a page prefix, such as `<name>View`, `<name>Dialog`, and `<name>FilterEntry`. `wait()` and `ready()` switch the root-window cursor. `filter_changed()`, `search()`, and `match()` implement common filtering. `addDialog()` and `propertiesDialog()` loop until subclass `add()` or `modify()` succeeds or the dialog is canceled. `deleteDialog()` asks for confirmation before calling subclass `delete()`. `on_local_clicked()` toggles between customized and all records.

## Control flow
Subclasses call the base constructor with their widget prefix and description, then provide page-specific `load()`, `dialogClear()`, `dialogInit()`, `add()`, `modify()`, and `delete()` methods. Menu and toolbar actions in the main window dispatch to these common methods on the current page. Row activation opens the properties dialog.

## State and persistence behavior
The base class tracks `self.local`, `self.view`, `self.dialog`, `self.filter_entry`, the root window, cursor objects, and the human-readable page description. It does not directly persist SELinux configuration; persistence is delegated to subclasses. UI state changes include current filter text, selected rows, dialog state, and local/all mode.

## Dependencies and integration points
The base depends on GTK and GDK from PyGObject, gettext, and widget IDs defined in `system-config-selinux.ui`. It is used by pages such as ports and users and is called indirectly by `system-config-selinux.py` menu/toolbar dispatch.

## Risks and edge cases
The class assumes subclasses initialize `self.filter` before filter signals fire. Blocking subclass operations still run in the GTK main thread; cursor changes are cosmetic and the UI can remain unresponsive. `match()` swallows all exceptions, which hides unexpected non-string data issues. Confirmation strings format before translation lookup, limiting translator flexibility. The default `use_menus()` returns true, so non-editable subclasses must override it.

## Test signals
Tests should exercise base dialog loops with subclass stubs, filter signal behavior, case-insensitive search/match, local/all toggle label and reload behavior, delete confirmation routing, and cursor state changes around mocked long-running operations.
