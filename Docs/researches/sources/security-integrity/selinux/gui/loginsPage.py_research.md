# sources/security-integrity/selinux/gui/loginsPage.py

## Purpose

`loginsPage.py` implements the GUI page for mapping Linux login names to SELinux users and MLS/MCS ranges.

## Important APIs And Methods

`loginsPage` extends `semanagePage`, uses `seobject.loginRecords()` to read login mappings and `seobject.seluserRecords()` to populate possible SELinux users. It writes changes through `semanage login`.

Important methods are `load(filter)`, `__dialogSetup()`, `dialogInit()`, `dialogClear()`, `add()`, `modify()`, and `delete()`.

## Control Flow

Initialization creates a three-column store for login name, SELinux user, and range, loads records, and stores dialog widgets. `load()` reads mappings, translates ranges, filters against login/user/range values, and selects the first row. `__dialogSetup()` lazily builds the SELinux user combo, omitting `system_u` and defaulting to `user_u`. Dialog initialization fills fields from the selected row and disables editing of existing login names. Add/modify/delete call `semanage login` with the selected user and range.

## State And Persistence

The page keeps UI store state and a `firstTime` flag for combo setup. Persistent changes are semanage login mappings. The code protects required `root` and `__default__` mappings from deletion.

## Dependencies And Integration Points

It depends on GTK, `seobject`, `semanagePage`, gettext, and `semanage`. UI IDs include `loginsNameEntry`, `loginsSelinuxUserCombo`, and `loginsMLSEntry`.

## Risks

Command strings interpolate login names, SELinux users, and ranges without shell quoting. `__dialogSetup()` assumes `user_u` exists and that the combo has at least one row. Broad gettext fallback hides localization issues. Deleting or modifying mappings requires privileges and may fail for policy-specific reasons surfaced only as command output.

## Test Signals

Tests should mock login and seluser records to verify filtering, default combo selection, delete protection for required mappings, range defaulting to `s0`, and semanage command strings for add/modify/delete.
