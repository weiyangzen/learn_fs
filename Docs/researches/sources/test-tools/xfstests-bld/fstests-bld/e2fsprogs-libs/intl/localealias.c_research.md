<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localealias.c -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localealias.c

## Purpose
This file implements locale alias expansion for gettext catalog lookup. It reads `locale.alias` files from configured alias paths, stores alias-value pairs, and performs case-insensitive lookup.

## Important APIs, Types, and Functions
The exported function is `_nl_expand_alias(const char *name)`. Static helpers are `read_alias_file(fname, fname_len)`, `extend_alias_table()`, and `alias_compare()`. Important data includes `struct alias_map`, `string_space`, `map`, `nmap`, `maxmap`, and static `locale_alias_path`.

## Control Flow
`_nl_expand_alias` initializes `locale_alias_path` from `LOCALE_ALIAS_PATH`, searches the sorted alias map with `bsearch`, and lazily reads additional `PATH_SEPARATOR`-delimited alias directories until a match is found or paths are exhausted. `read_alias_file` opens `<dir>/locale.alias`, parses two whitespace-delimited fields per non-comment line into pooled storage, grows the alias table as needed, ignores long trailing line fragments, and sorts the map after adding entries.

## State and Persistence
Alias mappings persist in process-global heap storage. In libc builds a lock protects map initialization and lookup. No files are written.

## Dependencies and Integration Points
It depends on `LOCALE_ALIAS_PATH`, optional `relocatable.h`, stdio, ctype, allocation, and `gettextP.h`. `finddomain.c` calls `_nl_expand_alias` before exploding locale names.

## Risks
Standalone builds lack real locking. Alias file parsing uses a fixed 400-byte line buffer and only reads the first two fields, which is intentional but can ignore unusual files. Allocation failure silently leaves partial alias data. Because alias values are returned from internal storage, callers must not free them.

## Test Signals
Use alias path fixtures with comments, blank lines, mixed-case aliases, duplicate aliases, long lines, multiple directories, missing files, and relocatable paths. Confirm bsearch lookup works after lazy loading and sorting.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localealias.c -->
