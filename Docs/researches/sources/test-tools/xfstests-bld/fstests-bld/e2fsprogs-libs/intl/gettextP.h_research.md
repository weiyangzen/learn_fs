<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettextP.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettextP.h

## Purpose
This private header defines the internal ABI and data structures for the embedded libintl implementation.

## Important APIs, Types, and Functions
Important macros include `internal_function`, `attribute_hidden`, `__builtin_expect`, `W`, `SWAP`, and `ZERO`. Core types are `struct sysdep_string_desc`, `struct loaded_domain`, and `struct binding`. It declares `_nl_msg_cat_cntr`, `_nl_locale_name`, `_nl_find_domain`, `_nl_load_domain`, `_nl_unload_domain`, `_nl_init_domain_conv`, `_nl_free_domain_conv`, and `_nl_find_msg`, plus public/internal gettext function prototypes.

## Control Flow
As a header, it does not execute. It selects libc versus standalone declarations, includes iconv/gconv support when available, and includes `libgnuintl.h` with redirection macros disabled so internal code can call real `libintl_*` names.

## State and Persistence
It describes process-global state rather than owning it. `struct loaded_domain` stores mapped catalog data, byte-swap flags, original/translated string tables, sysdep tables, hash tables, conversion state, and plural expression metadata. `struct binding` stores domain-specific directory and codeset state.

## Dependencies and Integration Points
It depends on `loadinfo.h`, `gmo.h`, optional iconv/gconv headers, and `libgnuintl.h`. Nearly every C file in `intl` includes it.

## Risks
Because this is private ABI, changes can break all gettext internals. The `ZERO` flexible-array compatibility macro relies on careful allocation sizing. Byte swapping and conversion fields must stay aligned with loader and lookup expectations.

## Test Signals
Compile the entire `intl` directory across standalone and libc-like configurations, with and without iconv, and run catalog lookup tests that exercise loaded-domain fields, bindings, sysdep strings, and plural metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/gettextP.h -->
