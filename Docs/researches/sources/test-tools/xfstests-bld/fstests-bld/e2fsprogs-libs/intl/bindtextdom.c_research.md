<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/bindtextdom.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/bindtextdom.c

## Purpose
This file implements GNU gettext domain binding APIs: `bindtextdomain` and `bind_textdomain_codeset` under either libc names or `libintl_`-prefixed standalone names.

## Important APIs, Types, and Functions
The central helper is `set_binding_values(domainname, dirnamep, codesetp)`. Public entry points are `BINDTEXTDOMAIN` and `BIND_TEXTDOMAIN_CODESET`, mapped to `__bindtextdomain`/`__bind_textdomain_codeset` in libc or `libintl_bindtextdomain`/`libintl_bind_textdomain_codeset` outside libc. It manipulates `struct binding` from `gettextP.h`, `_nl_domain_bindings`, `_nl_default_dirname`, `_nl_msg_cat_cntr`, and `_nl_state_lock`.

## Control Flow
Invalid empty domain names return `NULL`. Otherwise the helper locks global gettext state, searches the sorted binding list, returns current values for query calls, replaces changed directory/codeset strings for existing bindings, or allocates and inserts a new sorted binding. Codeset changes increment `codeset_cntr`; any binding modification increments `_nl_msg_cat_cntr` to invalidate cached translations.

## State and Persistence
State is in the process-global `_nl_domain_bindings` linked list. Directory and codeset strings may be dynamically allocated and later reused by lookup code in `dcigettext.c`. No filesystem persistence occurs.

## Dependencies and Integration Points
It depends on `gettextP.h`, `libgnuintl.h` or system `libintl.h`, libc lock macros in glibc builds, and the central lookup/cache code that watches `_nl_msg_cat_cntr` and `codeset_cntr`.

## Risks
Standalone builds use dummy locks, so the included libintl is not truly thread-safe outside glibc. Allocation failure returns `NULL` through output pointers without errno-specific reporting. Pointer comparison against `_nl_default_dirname` is used to decide whether to free directory strings, so callers must not mutate returned pointers.

## Test Signals
Test binding creation, querying, rebinding to the same value, rebinding to a new directory, setting/changing codesets, invalid domains, and confirming `_nl_msg_cat_cntr` changes only on real modifications.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/bindtextdom.c -->
