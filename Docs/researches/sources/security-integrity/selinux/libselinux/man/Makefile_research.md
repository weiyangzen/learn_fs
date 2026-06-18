# sources/security-integrity/selinux/libselinux/man/Makefile

## Purpose
This makefile installs libselinux manual pages for sections 3, 5, and 8, including optional localized man pages.

## Important APIs, types, and functions
Variables include `LINGUAS`, `PREFIX`, `MANDIR`, `MAN3SUBDIR`, `MAN5SUBDIR`, `MAN8SUBDIR`, and derived install directories. `install` creates section directories, installs `man3/*.3`, `man5/*.5`, and `man8/*.8`, then loops through each language in `LINGUAS` and installs localized section files if the language section directory exists. `all`, `relabel`, `format`, `distclean`, and `clean` are present but empty.

## Control flow
Running `make install` performs base English installation first, then iterates languages and conditionally creates/copies localized man pages per section.

## State and persistence behavior
Persistent effects are installed man-page files under `$(DESTDIR)$(MANDIR)` and localized subdirectories. No source files are generated or cleaned by this makefile.

## Dependencies and integration points
It is invoked from the top-level libselinux makefile and depends on shell conditionals, `mkdir`, and `install`. It integrates with packaging variables for prefix, man section subdirectory names, and selected localization list.

## Risks and edge cases
Empty globs such as `man3/*.3` can cause install failures if a section has no files. Localized installation only checks directory existence, not whether matching files exist. Empty clean/format targets may surprise maintainers expecting generated man artifacts to be removed or formatted.

## Test signals
Tests should install to a staging `DESTDIR`, verify base and localized section paths, run with empty and nonempty `LINGUAS`, check custom man subdir variables, and validate behavior when a localized section directory exists but has no matching pages.
