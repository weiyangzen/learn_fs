# sources/security-integrity/selinux/gui/po/Makefile

## Purpose

This Makefile builds, refreshes, installs, and reports on gettext translation catalogs for the GUI package.

## Targets And Flow

Variables define `NLSPACKAGE=gui`, `POTFILE=gui.pot`, install helpers, locale destination, and gettext tools. `PO_LINGUAS` is discovered from `*.po`; `LINGUAS` can limit the build; otherwise all discovered languages are built. `all` builds `.mo` files. `$(POTFILE)` runs `xgettext` over files listed in `POTFILES`. `refresh-po` merges each `.po` with the pot file. `clean` removes `.mo`, backups, `.depend`, and `tmp`. `install` places compiled catalogs as `selinux-gui.mo` under each language's `LC_MESSAGES`. `report` runs `msgfmt --statistics`.

## State And Persistence

Build outputs are `.mo` files in the source directory. Installed state is locale catalog files under `$(PREFIX)/share/locale/<lang>/LC_MESSAGES/selinux-gui.mo`.

## Dependencies And Integration Points

It depends on gettext tools `xgettext`, `msgmerge`, and `msgfmt`, a `POTFILES` manifest, and the parent GUI Makefile. Runtime Python modules use gettext domain `selinux-gui`, matching the installed catalog name.

## Risks

If `POTFILES` is stale, strings will be missed. The package variable is `gui` while the installed message catalog is `selinux-gui.mo`; this is intentional through the install rule but can confuse maintainers. `LINGUAS` filtering is make-pattern based and should be tested for partial language names.

## Test Signals

Useful checks include successful `make all`, `make report`, installing catalogs for selected `LINGUAS`, and runtime gettext lookup of translated GUI strings.
