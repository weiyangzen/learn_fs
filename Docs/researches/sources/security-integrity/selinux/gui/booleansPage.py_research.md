# sources/security-integrity/selinux/gui/booleansPage.py

## Purpose

`booleansPage.py` implements the GTK page for viewing, filtering, toggling, deleting, and reverting SELinux booleans in `system-config-selinux`.

## Important APIs, Types, And Methods

`Modifier` and `Boolean` are tiny state wrappers, but the page primarily uses GTK `ListStore`, `TreeView`, `CellRendererToggle`, and `CellRendererText`. Columns are `ACTIVE`, `MODULE`, `DESC`, and `BOOLEAN`. The page uses `seobject.booleanRecords()` for reads and command-line tools for writes.

Key methods are `load(filter)`, `match(key, filter)`, `boolean_toggled(widget, row)`, `deleteDialog()`, `on_revert_clicked()`, `on_local_clicked()`, `filter_changed()`, `wait()`, `ready()`, and `error()`.

## Control Flow

Initialization obtains widgets from the UI object, wires filter events, sets up columns and sorting, configures the toggle renderer, and calls `load()`. `load()` rebuilds the store from `booleanRecords().get_all(self.local)`, filtering by boolean name, category, or description. Toggling a row immediately updates the model, runs `/usr/sbin/setsebool -P name value`, reloads the store, and restores the cursor. Delete and revert use `semanage boolean -d` and `semanage boolean --deleteall`.

## State And Persistence

UI state includes the current filter, local/customized mode, cursor state, and the list store. Persistent SELinux state changes are made by `setsebool -P` and `semanage boolean` commands, modifying the local policy store.

## Dependencies And Integration Points

The page depends on PyGObject GTK/GDK, `seobject`, `semanagePage.idle_func`, gettext, `/usr/sbin/setsebool`, and `semanage`. It integrates with a Glade/GTK UI that must provide object IDs such as `mainWindow`, `booleansFilter`, `booleansView`, and `booleanRevertButton`.

## Risks

Command strings interpolate boolean names without shell quoting, relying on trusted boolean names from SELinux policy. Broad `except` blocks in gettext and `match()` can hide errors. The UI updates the checkbox before command success and then reloads, which is acceptable but can briefly show failed state. `deleteDialog()` and revert operations require privileges and surface failures through dialogs.

## Test Signals

Unit tests can mock `seobject.booleanRecords` and `getstatusoutput` to verify filtering, local-mode toggling, command generation, and reload behavior. GUI integration tests should verify columns, sorting, search, and error dialogs for failed commands.
