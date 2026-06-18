# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_meta.c

This file contains Check unit tests for libgfs2 metadata description tables.

Test cases:
- `check_metadata_sizes()` walks every `lgfs2_metadata` entry, verifies each field offset is contiguous from zero, and verifies final offset equals metadata size.
- `check_symtab()` verifies fields marked as mask/enum have a symbol table, and fields with symbol tables carry mask/enum flags.
- `check_flag_sym_value()` verifies `lgfs2_flag_sym_value()` returns zero for null/empty/invalid names and returns exact constants for all known `GFS2_DIF_*` dinode flags.
- `check_ptrs()` verifies fields marked as pointers have nonzero `points_to`, and non-pointer fields do not.

`suite_meta()` groups these tests under “Metadata description checks”.

The file depends on `libgfs2.h` metadata descriptors and the Check framework. It validates internal metadata introspection consistency rather than on-disk I/O.
