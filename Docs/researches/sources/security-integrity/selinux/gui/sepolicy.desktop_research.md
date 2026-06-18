# sources/security-integrity/selinux/gui/sepolicy.desktop

## Purpose
This desktop entry exposes the `sepolicy gui` policy management interface in desktop menus under "SELinux Policy Management Tool".

## Important APIs, types, and functions
Important fields are `Name`, `Comment`, `Icon=sepolicy`, `Exec=/usr/bin/sepolicy gui`, `Type=Application`, `Terminal=false`, `Categories=System;Security;`, and `Keywords=policy;security;selinux;avc;permission;mac;`. It contains no localized strings beyond the default English fields.

## Control flow
A desktop shell reads the metadata and launches `/usr/bin/sepolicy gui`. The executable then owns all GUI behavior.

## State and persistence behavior
The file is static application metadata and stores no runtime state. Persistence depends on package installation and desktop database indexing.

## Dependencies and integration points
It depends on the `sepolicy` executable supporting the `gui` argument and on an icon named `sepolicy`. It integrates with freedesktop application menus and search through categories and keywords.

## Risks and edge cases
Launch fails if `sepolicy` is not installed at `/usr/bin/sepolicy`. The desktop entry does not request a terminal or privilege wrapper, so any authorization must be handled by `sepolicy gui` itself. Lack of localized fields may reduce usability in non-English locales.

## Test signals
Run `desktop-file-validate`, confirm the command and icon exist after install, and smoke-test menu launch in a graphical session.
