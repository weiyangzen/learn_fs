<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/po/Makefile -->
# sources/security-integrity/selinux/policycoreutils/po/Makefile

## Purpose
Builds and installs gettext catalogs for the `policycoreutils` package.

## Important APIs, Types, And Functions
The file defines `NLSPACKAGE=policycoreutils`, `POTFILE`, gettext commands (`xgettext`, `msgmerge`, `msgfmt`), `PO_LINGUAS`, `USER_LINGUAS`, `USE_LINGUAS`, `POFILES`, `MOFILES`, and `POTFILES` read from the local `POTFILES` manifest. Targets include `all`, `refresh-po`, `clean`, `install`, `report`, `relabel`, and `test`.

## Control Flow
`all` regenerates the POT template and compiles selected `.po` files into `.mo` files. `$(POTFILE)` runs `xgettext` over the files listed in `POTFILES`, replacing the old template only when it differs. `refresh-po` merges each language with the new POT. `install` places compiled catalogs under `$(DESTDIR)$(PREFIX)/share/locale/<lang>/LC_MESSAGES/policycoreutils.mo`.

## State And Persistence
The build produces `.mo`, temporary `.pot`, and generated `.po`/`.pot` files. Installation persists translation catalogs into the filesystem image.

## Dependencies And Integration Points
Depends on gettext tooling and the package-wide `LINGUAS` selection. It is called from the parent policycoreutils make recursion.

## Risks And Edge Cases
An incomplete `POTFILES` manifest misses translatable strings. Invalid `LINGUAS` silently falls back to all languages. Install paths depend on `PREFIX` and `DESTDIR`.

## Test Signals
`make report` runs `msgfmt --statistics` for catalog health; successful `all` and `install` indicate gettext tools and locale paths are usable.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/po/Makefile -->
