# sources/security-integrity/selinux/gui/polgengui.py

## Purpose
`polgengui.py` implements the GTK 3 wizard for generating SELinux policy modules. It collects a policy type, application or user name, executable/init-script paths, transition/admin roles, network port permissions, file write locations, and custom booleans, then drives `sepolicy.generate.policy` to emit policy files into a selected output directory.

## Important APIs, types, and functions
The main type is `childWindow`, whose page constants map logical wizard steps onto notebook page indexes from `/usr/share/system-config-selinux/polgen.ui`. `get_all_modules()` shells out to `semodule -l` to detect already-loaded module names. `get_type()` maps radio buttons to `sepolicy.generate` constants. `generate_policy()` is the core handoff into `sepolicy.generate.policy`: it adds booleans, sets application helper flags, selected transitions/admin roles, network settings, writable files/directories, and calls `generate(outputdir)`. UI helpers include `forward()`, `back()`, `setupScreen()`, `exec_select()`, `init_script_select()`, `add()`, `add_dir()`, and validation hooks for names and ports.

## Control flow
Module import initializes gettext, appends the system-config-selinux install path, builds a global `Gtk.Builder`, and loads `polgen.ui`. Standalone execution installs the default SIGINT handler, constructs `childWindow`, calls `setupScreen()`, shows the main window, and enters `Gtk.main()`. Within the wizard, `forward()` validates the current page before advancing through the per-policy page list in `self.pages`. The finish page calls `generate_policy()` and changes the cancel button to close. Name validation also pre-populates executable or init-script paths when files matching the entered name exist in standard locations.

## State and persistence behavior
Runtime state is held in GTK widgets, `Gtk.ListStore` instances, `self.pages`, `self.current_page`, selected tree rows, and the cached module/type/role/user lists from `sepolicy.generate`. Persistent effects occur only when `sepolicy.generate.policy.generate()` writes policy artifacts into the chosen output directory. The script reads installed policy data through `sepolicy`, installed modules through `semodule`, and local filesystem paths for candidate executables.

## Dependencies and integration points
This file depends on PyGObject GTK 3, `sepolicy`, `sepolicy.generate`, `sepolicy.interface`, `semodule`, gettext domain `selinux-gui`, and a fixed UI path under `/usr/share/system-config-selinux`. It integrates with the wider GUI through desktop launchers and with SELinux policy generation through the `sepolicy.generate` Python API.

## Risks and edge cases
Several exception handlers use `e.message`, which is not valid on normal Python 3 `Exception` objects. `on_existing_user_page_next()` checks `self.view` rather than `existing_user_treeview`, so existing-user selection validation appears wrong. The wizard relies on fixed installed UI paths and will fail before constructing a window if `polgen.ui` is absent. Name validation allows only alphanumeric values, which may reject valid SELinux naming patterns but prevents spaces. Port validation is delegated to `sepolicy.generate.verify_ports()`. The generated policy behavior depends heavily on `sepolicy.generate` internals, so tests need version-compatible bindings.

## Test signals
Useful tests cover wizard page ordering for every `sepolicy.generate` policy type, invalid and valid names, executable and init-script auto-fill, inbound/outbound port validation, boolean/file/dir list mutation, transition and role selection propagation, duplicate module/type warning paths, and `generate_policy()` interactions with a mocked `sepolicy.generate.policy`.
