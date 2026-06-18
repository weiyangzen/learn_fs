# sources/security-integrity/selinux/gui/selinux-polgengui.desktop

## Purpose
This desktop entry exposes the SELinux policy generation GUI in desktop application menus. It labels the tool as "SELinux Policy Generation Tool" and describes it as a way to generate SELinux policy modules.

## Important APIs, types, and functions
The file is freedesktop `.desktop` metadata rather than executable code. Key fields are `Name`, localized `Name[...]` translations, `Comment`, localized `Comment[...]` translations, `StartupNotify=true`, `Icon=system-config-selinux`, `Exec=/usr/bin/selinux-polgengui`, `Type=Application`, `Terminal=false`, and `Categories=System;Security;`.

## Control flow
Desktop shells parse this file, show the localized name/comment where possible, and invoke `/usr/bin/selinux-polgengui` when the user launches the item. There is no internal branching; control transfers to the installed launcher or GUI script.

## State and persistence behavior
The entry stores static launch metadata and translation strings. It does not persist runtime state. Installation into an applications directory determines menu visibility, and the `Exec` path determines which binary or wrapper is launched.

## Dependencies and integration points
It integrates with freedesktop-compliant menu systems, icon themes providing `system-config-selinux`, and the installed `/usr/bin/selinux-polgengui` command. It complements `polgengui.py` and the shell wrapper/package layout that installs the executable.

## Risks and edge cases
If `/usr/bin/selinux-polgengui` or the icon is missing, menu launch fails or displays a generic icon. The entry has no privilege escalation field, so elevation behavior depends on the launched command. Localized strings are static and can become stale relative to the English name/comment.

## Test signals
Validation should run `desktop-file-validate`, confirm the `Exec` target exists after packaging, verify the icon resolves, and smoke-test launch in a graphical session with the expected gettext locale.
