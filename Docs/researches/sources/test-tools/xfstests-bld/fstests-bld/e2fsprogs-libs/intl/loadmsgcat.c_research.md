<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadmsgcat.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadmsgcat.c

## Purpose
This file loads GNU `.mo` message catalogs into memory, validates file format revisions, sets up hash/sysdep tables, initializes charset conversion, extracts plural expressions, and frees loaded domains in libc builds.

## Important APIs, Types, and Functions
Important functions are `_nl_load_domain`, `_nl_init_domain_conv`, `_nl_free_domain_conv`, `_nl_unload_domain`, and static `get_sysdep_segment_value`. It defines global `_nl_msg_cat_cntr`. It uses `struct mo_file_header`, `struct loaded_domain`, `struct loaded_l10nfile`, `struct binding`, `struct sysdep_*`, `EXTRACT_PLURAL_EXPRESSION`, iconv/gconv handles, and optional mmap.

## Control Flow
`_nl_load_domain` marks the l10n file decided, opens the filename, stats it, maps or reads it, validates magic and supported major revision, allocates `loaded_domain`, sets byte-swap flags and string/hash table pointers, and handles minor revision sysdep strings by resolving supported system-dependent format fragments and building in-memory descriptor/hash tables. It then initializes charset conversion from the header entry and extracts plural metadata. Invalid files unwind allocated/mapped memory and leave `domain_file->data` null.

## State and Persistence
Loaded catalog state persists in `domain_file->data` as a `loaded_domain`. It may reference mmaped file data, malloced file data, extra sysdep memory, conversion tables, and plural expression trees. No files are written.

## Dependencies and Integration Points
It depends on filesystem APIs (`open`, `read`, `fstat`, `mmap`), `.mo` layout from `gmo.h`, private structures from `gettextP.h`, hashing from `hash-string.h`, plural parsing from `plural-exp.h`, locale charset from `localcharset.c`, and optional iconv/gconv conversion. `dcigettext.c` calls `_nl_find_msg`, which uses data initialized here.

## Risks
The loader reads binary catalog files and must defend against malformed offsets, unsupported revisions, and allocation failures. Some paths allocate data before later validation. Charset conversion caches can be invalidated by `bind_textdomain_codeset`. Sysdep string support is complex and depends on exact hash-table behavior. Standalone builds may leak loaded catalogs until process exit.

## Test Signals
Load valid and invalid `.mo` fixtures, swapped-endian files, revision 0 and revision 1 sysdep catalogs, catalogs with and without hash tables, malformed sysdep references, charset headers requiring iconv, missing charset headers, and plural headers with multiple `nplurals` values.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/loadmsgcat.c -->
