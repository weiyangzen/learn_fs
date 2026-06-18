# sources/security-integrity/selinux/gui/system-config-selinux.ui

## Purpose
`system-config-selinux.ui` is the GTK Builder/Glade definition for the main SELinux administration GUI. It declares the application window, menus, navigation tree, hidden notebook pages, toolbars, dialogs, list views, combo models, labels, accelerators, and translatable text consumed by the Python page modules.

## Important APIs, types, and functions
The file is declarative XML requiring GTK 3. Important objects include `mainWindow`, `aboutWindow`, `selectView`, `notebook`, status widgets (`enabledOptionMenu`, `currentOptionMenu`, `selinuxTypeOptionMenu`, `relabelCheckbutton`), page views (`booleansView`, `fcontextView`, `loginsView`, `usersView`, `portsView`, `modulesView`, `domainsView`), filter entries, semanage dialogs (`loginsDialog`, `portsDialog`, `fcontextDialog`, `usersDialog`), and action widgets wired to handlers such as `on_add_clicked`, `on_properties_clicked`, `on_delete_clicked`, `on_local_clicked`, and `on_about_activate`.

## Control flow
`Gtk.Builder.add_from_file()` loads the XML, then `connect_signals()` in `system-config-selinux.py` and page constructors bind handlers. The navigation tree in Python selects hidden notebook pages by index. Toolbars and menus emit shared actions, and the active page object interprets those actions.

## State and persistence behavior
The XML stores static UI structure, default widget properties, list-store seed data such as TCP/UDP and SELinux mode choices, translations, tooltips, and response codes. Runtime state is held by GTK object instances created from this definition; persistent SELinux changes are performed by Python code responding to its signals.

## Dependencies and integration points
It integrates tightly with all GUI Python modules through exact widget IDs. It depends on GTK 3 classes, stock icon identifiers, translation extraction from `translatable="yes"` properties, and image/icon assets such as `system-config-selinux.png`.

## Risks and edge cases
Python modules assume these IDs and notebook ordering remain stable, so UI edits can silently break page binding. Some GTK stock and `GtkImageMenuItem` patterns are legacy in newer GTK 3 environments. The `delete_menu_item` defines an accelerator but no explicit activate signal in the XML, while toolbar delete buttons do connect. Dialog titles and labels must match page semantics; stale labels can confuse operations such as file contexts versus login mappings.

## Test signals
Tests should load the UI through `Gtk.Builder` in a graphical or headless GTK test environment, assert all Python-referenced object IDs exist with expected classes, verify signal names resolve, check notebook page order against `system-config-selinux.py`, and run accessibility/translation checks for visible labels and tooltips.
