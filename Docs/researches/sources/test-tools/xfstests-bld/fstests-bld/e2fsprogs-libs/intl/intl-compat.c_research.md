<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/intl-compat.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/intl-compat.c

## Purpose
This compatibility file exports unprefixed gettext symbols that forward to the `libintl_`-prefixed implementations, preserving compatibility with older gettext tests and allowing preload-style usage.

## Important APIs, Types, and Functions
It defines forwarding functions for `gettext`, `dgettext`, `dcgettext`, `ngettext`, `dngettext`, `dcngettext`, `textdomain`, `bindtextdomain`, and `bind_textdomain_codeset`. On MSVC DLL builds, `DLL_EXPORTED` marks them for export.

## Control Flow
The file undefines possible macro redirections, then each function directly returns the corresponding `libintl_*` call result.

## State and Persistence
No local state. All behavior is delegated to shared libintl internals.

## Dependencies and Integration Points
It depends on `gettextP.h`, which exposes the prefixed functions. It is compiled into `libintl`/`libgnuintl` by `intl/Makefile.in`.

## Risks
Exporting unprefixed symbols can collide with libc or platform libintl implementations if linking is not controlled. The file exists specifically for compatibility, so removing it can break old Autoconf gettext probes.

## Test Signals
Link a small program against the included library using unprefixed gettext calls and confirm the symbols resolve to the same behavior as prefixed calls.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/intl-compat.c -->
