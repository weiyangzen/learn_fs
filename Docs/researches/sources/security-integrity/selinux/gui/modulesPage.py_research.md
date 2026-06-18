# sources/security-integrity/selinux/gui/modulesPage.py

## Purpose

`modulesPage.py` implements the GUI page for listing, installing, removing, and audit-toggling SELinux policy modules.

## Important APIs And Methods

`modulesPage` extends `semanagePage`. It uses `Popen("semodule -lfull", shell=True)` to list modules, `semodule -X <priority> -r <module>` to remove modules, `semodule -i <file>` to install modules, `semodule -DB` to disable dontaudit rules, `semodule -B` to rebuild and restore audit behavior, and `selinux.selinux_getpolicytype()` to read policy type.

Key methods are `load(filter)`, `sort_int()`, `new_module()`, `delete()`, `enable_audit()`, `disable_audit()`, `addDialog()`, and `add(file)`.

## Control Flow

Initialization builds a three-column model for module name, priority, and kind; wires filter, audit, and new-module buttons; sets a custom sort function for priority; reads policy type; and loads module data. `load()` parses each `semodule -lfull` line into priority/module/kind, filters, and inserts rows. `addDialog()` opens a file chooser limited to `*.pp`, and `add()` installs the selected module. `new_module()` launches `selinux-polgengui`.

## State And Persistence

UI state includes the module list and `audit_enabled` flag. Persistent state changes include module installation/removal and semodule rebuilds. Audit toggling changes whether dontaudit rules are active in the loaded policy until rebuilt.

## Dependencies And Integration Points

The page depends on GTK, `selinux`, `semanagePage`, `semodule`, and `selinux-polgengui`. It integrates with the policy generation UI and with package-installed module files.

## Risks

`sort_int()` appears to read both `p1` and `p2` from `iter1`, so numeric priority sorting will always compare equal. `load()` uses shell execution and broad `except: pass`, hiding parse or command failures. Removal builds a shell string from module and priority values parsed from command output. Installing modules executes a user-selected file path through argument-list `Popen`, which is safer. Audit button label changes before checking command success, so failure can leave misleading UI state.

## Test Signals

Tests should verify parsing of `semodule -lfull`, filtering, add/remove command calls, audit toggle behavior on success and failure, file chooser filtering, and a regression test for the `sort_int()` iterator bug.
