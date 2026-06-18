# sources/security-integrity/selinux/gui/portsPage.py

## Purpose
`portsPage.py` implements the "Network Port" management page for the SELinux configuration GUI. It displays SELinux port type mappings, supports list and grouped views, filters rows, and adds, modifies, or deletes port mappings through `semanage port`.

## Important APIs, types, and functions
`portsPage` extends `semanagePage`. Column constants define the `Gtk.ListStore` layout: SELinux type, protocol, MLS/MCS level, and port/range. `init_store()` creates the table columns and numeric range sorting. `load()` reads individual records from `seobject.portRecords().get_all(self.local)`. `group_load()` reads grouped records from `get_all_by_type()`. `dialogInit()` and `dialogClear()` synchronize selected rows with the edit dialog. `add()`, `modify()`, and `delete()` run `semanage port -a`, `-m`, and `-d` via `getstatusoutput()`. `on_group_clicked()` toggles between editable list view and read-only grouped view.

## Control flow
Construction wires the group button, filter entry, protocol combo, dialog entries, and action buttons, then initializes the store and loads current records. Filtering calls either `load()` or `group_load()` based on the current mode. Add/modify/delete operations set the busy cursor through the base class, run the external command, restore the cursor, update the in-memory store, and report command output on failure.

## State and persistence behavior
The page keeps display state in `self.store`, `self.filter`, `self.group`, `self.edit`, selected tree rows, and dialog widgets. Persistent system changes are not made through libsemanage bindings directly; they are delegated to the `semanage port` CLI, which updates SELinux local policy configuration. Group view is display-only and disables add/properties/delete buttons while active.

## Dependencies and integration points
The file depends on GTK/GObject, `seobject.portRecords`, the base `semanagePage`, gettext domain `selinux-gui`, and the `semanage` command. It is added by `system-config-selinux.py` when SELinux is enabled and relies on widget IDs from `system-config-selinux.ui`.

## Risks and edge cases
The `semanage` command strings interpolate user-controlled type, MLS, and port values into a shell command; only port characters are lightly checked and the range bounds are not validated. Type and MLS values are not shell-quoted. Empty port input becomes `1`, which may surprise users. Group toggle sensitivity is based on the previous `self.group` value before flipping, so the first transition intentionally disables editing but is easy to misread. Error handling preserves command text but not structured error causes.

## Test signals
Tests should mock `seobject.portRecords` and `getstatusoutput()` to verify list/group loading, filtering across type/protocol/MLS/port fields, numeric sorting of ranges, add/modify/delete command construction, rejection of nonnumeric ranges, button sensitivity in grouped mode, and UI-store refresh after successful operations.
