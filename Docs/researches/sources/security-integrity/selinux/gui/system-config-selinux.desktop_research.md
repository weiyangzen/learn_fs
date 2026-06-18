# sources/security-integrity/selinux/gui/system-config-selinux.desktop

## Purpose
This desktop entry exposes the main graphical SELinux administration application in desktop menus under "SELinux Management".

## Important APIs, types, and functions
The `.desktop` fields include localized `Name[...]` and `Comment[...]` values, `StartupNotify=true`, `Icon=system-config-selinux`, `Exec=/usr/bin/system-config-selinux`, `Type=Application`, `Terminal=false`, and `Categories=System;Security;`.

## Control flow
Desktop shells parse the file, display a localized menu item, and invoke `/usr/bin/system-config-selinux`. That wrapper then delegates privilege handling to `pkexec` and starts `system-config-selinux.py`.

## State and persistence behavior
The file is static launch metadata. It does not store application settings or SELinux state; it only determines how the GUI appears and starts.

## Dependencies and integration points
It integrates with freedesktop menu systems, the installed launcher at `/usr/bin/system-config-selinux`, the `system-config-selinux` icon asset, and PolicyKit through the wrapper.

## Risks and edge cases
Missing launcher or icon resources cause failed launches or degraded menu presentation. Localized strings must remain synchronized with the application's role. The entry does not define keywords, which may reduce menu search discoverability compared with `sepolicy.desktop`.

## Test signals
Use `desktop-file-validate`, verify installed `Exec` and icon targets, and perform a menu launch smoke test through a graphical session with PolicyKit.
