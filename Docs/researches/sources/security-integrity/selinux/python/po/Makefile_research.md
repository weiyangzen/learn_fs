<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/po/Makefile -->
# sources/security-integrity/selinux/python/po/Makefile

## Purpose
Builds and installs gettext catalogs for SELinux Python tools.

## Important APIs, Types, And Functions
Defines `NLSPACKAGE=python`, gettext command variables, selected language lists, `POFILES`, `MOFILES`, and `POTFILES`. Targets are `all`, `$(POTFILE)`, `refresh-po`, `clean`, `install`, `report`, `relabel`, and `test`.

## Control Flow
`all` compiles `.po` files into `.mo` files. The POT target runs Python-aware `xgettext` over `POTFILES`, joins additional strings from the sepolicy Glade file, and replaces the POT only when changed. `refresh-po` merges translations. `install` writes catalogs as `selinux-python.mo` under locale directories.

## State And Persistence
Produces `.mo` files and may refresh `.po` catalogs. Install persists locale catalogs under `$(PREFIX)/share/locale`.

## Dependencies And Integration Points
Depends on gettext tools, a local `POTFILES` manifest, and `../sepolicy/sepolicy/sepolicy.glade` for GUI strings.

## Risks And Edge Cases
The package name `python` maps to installed catalog `selinux-python.mo`, so runtime domains must match. Missing Glade file or POTFILES entries can drop translations.

## Test Signals
`make report`, successful `msgfmt`, successful POT refresh, and runtime gettext lookup in Python tools.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/po/Makefile -->
