<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/Makefile.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/Makefile.in

## Purpose
This is the generated GNU gettext `intl` directory make template. It builds either included `libintl`/`libgnuintl`, generates headers and alias sed scripts, installs runtime support files when appropriate, and handles distribution/cleanup for the embedded gettext runtime.

## Important APIs, Types, and Functions
Important variables include `PACKAGE`, `VERSION`, `USE_INCLUDED_LIBINTL`, `BUILD_INCLUDED_LIBINTL`, `LTV_CURRENT`, `LTV_REVISION`, `LTV_AGE`, `OBJECTS`, `HEADERS`, `SOURCES`, `DISTFILES.*`, `DEFS`, `COMPILE`, and `INCLUDES`. Important targets include `all-yes`, `all-no-yes`, `libintl.$la`, `libgnuintl.$la`, object `.lo` rules, `libgnuintl.h`, `libintl.h`, `charset.alias`, `install`, `uninstall`, `dist`, `clean`, `distclean`, and tag/id targets.

## Control Flow
`all` dispatches based on configure substitutions. If included libintl is used, it builds `libintl`, generated headers, charset aliases, and sed scripts. If not, but gettext tools need an included helper, it builds `libgnuintl`. Install logic is heavily conditional on `PACKAGE` and `USE_INCLUDED_LIBINTL`: runtime installs headers/libraries, updates `charset.alias` and `locale.alias` via `ref-add.sed`, and gettext-tools installs source support files. Uninstall reverses alias references via `ref-del.sed`.

## State and Persistence
Build products include `.lo`, `.la`, static archives, `libgnuintl.h`, `libintl.h`, `charset.alias`, `ref-add.sed`, `ref-del.sed`, `.libs`, and tag/index files. Install persists libraries, headers, alias files, and optional gettext source support files under configured `libdir`, `includedir`, `localedir`, and `gettextsrcdir`.

## Dependencies and Integration Points
It depends on libtool, compiler/linker tools, `config.charset`, `ref-add.sin`, `ref-del.sin`, generated `plural.c`, and the C sources in this `intl` directory. It is configured by `configure.in` through gettext macros and is consumed by the top-level build when `AM_GNU_GETTEXT` selects included libintl.

## Risks
The template contains many legacy compatibility branches and generated substitutions, so stale configure values can break library naming or install behavior. Alias-file edits are global to install roots and must be reference-counted correctly. The target list includes `.c` files inside `HEADERS` for printf helpers, which is unusual but intentional for distribution dependencies.

## Test Signals
Build with included and system gettext modes, verify the selected library target is built, ensure `libgnuintl.h` substitutions remove `@HAVE_*@` placeholders, run `make install DESTDIR=...` and `make uninstall DESTDIR=...`, and confirm alias files are added/removed idempotently.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/Makefile.in -->
