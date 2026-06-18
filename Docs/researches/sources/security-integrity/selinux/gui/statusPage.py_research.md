# sources/security-integrity/selinux/gui/statusPage.py

## Purpose
`statusPage.py` implements the SELinux status page for the GUI. It displays and changes current enforcing mode, configured boot-time SELinux mode, configured policy type, and whether a filesystem relabel should be requested on next reboot.

## Important APIs, types, and functions
`statusPage` uses constants `ENFORCING`, `PERMISSIVE`, `DISABLED`, `modearray`, `SELINUXDIR`, and `RELABELFILE`. `get_current_mode()` reads runtime state using `selinux.is_selinux_enabled()` and `selinux.security_getenforce()`. `set_current_mode()` calls `selinux.security_setenforce()`. `read_selinux_config()` populates configured mode and available policy types. `write_selinux_config()` rewrites `selinux.selinux_path() + "config"` through a `.bck` file and rename. `on_relabel_toggle()` creates or removes `/.autorelabel`.

## Control flow
Construction binds status widgets from the GTK builder, initializes relabel state, populates current-mode choices based on runtime SELinux status, reads `/etc/selinux` policy directories, and connects mode/type signal handlers. Changing policy type prompts because it requires relabeling, toggles relabel when accepted, writes config, and updates history. Changing configured enabled mode prompts for disabling or re-enabling scenarios and writes the new config.

## State and persistence behavior
Runtime state is kept in widget selections plus `initialtype`, `initEnabled`, `enabled`, `types`, and `typeHistory`. Persistent effects include writing the SELinux config file, setting runtime enforce mode through selinuxfs, and creating/removing `/.autorelabel`.

## Dependencies and integration points
The page depends on PyGObject GTK, Python `selinux` bindings, `/etc/selinux`, selinuxfs, and the widget IDs from `system-config-selinux.ui`. It is always added by `system-config-selinux.py`, even when SELinux is disabled, but current-mode controls are disabled if SELinux is not active.

## Risks and edge cases
The file requires sufficient privileges to write `/etc/selinux/config`, call `security_setenforce`, and touch `/.autorelabel`. `write_selinux_config()` does not fsync and only rewrites existing `SELINUX=` and `SELINUXTYPE=` lines. The code assumes `selinux_getpolicytype()` and `selinux_getenforcemode()` Python bindings return tuple-like values. Relabel changes are made immediately when the checkbox toggles, including toggles triggered programmatically after warning dialogs.

## Test signals
Tests should mock `selinux` bindings and filesystem calls to cover enabled/permissive/disabled initialization, config rewrite behavior, policy-type list population, relabel file creation/removal, warning-dialog rejection restoring previous values, and permission-error reporting.
