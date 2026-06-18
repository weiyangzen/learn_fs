# File Research: sources/local-fs/ntfs-3g/libntfs-3g/collate.c

## Role

Implements NTFS index collation functions and the dispatcher that maps NTFS `COLLATION_RULES` values to comparison callbacks. This is used by index lookup/insertion code to order keys in NTFS B+tree indexes.

## Main Functions

- `ntfs_collate_binary()` compares arbitrary byte buffers with `memcmp()`, using length as a tiebreaker.
- `ntfs_collate_ntofs_ulong()` compares two little-endian 32-bit integers; rejects lengths other than 4.
- `ntfs_collate_ntofs_ulongs()` compares equal-length arrays of little-endian 32-bit integers; requires positive length and 4-byte alignment.
- `ntfs_collate_ntofs_security_hash()` compares security hash keys made of two little-endian 32-bit values.
- `ntfs_collate_file_name()` compares `FILE_NAME_ATTR` names using `ntfs_names_full_collate()` with the volume upcase table.
- `ntfs_get_collate_function()` returns the appropriate comparator for supported collation rules.

## Dependencies

Uses NTFS layout/index types from `attrib.h`, `index.h`, `collate.h`, Unicode collation helpers from `unistr.h`, and logging from `logging.h`.

## Important Behavior

The filename comparator ignores the explicit data lengths and trusts `FILE_NAME_ATTR.file_name_length`. Numeric comparators validate fixed lengths and return `NTFS_COLLATION_ERROR` on malformed keys. Unsupported collation rules set `errno = EOPNOTSUPP` and return `NULL`.

## Research Notes

This file is a small but central dispatch layer: `index.c` depends on it through `ntfs_get_collate_function()` for every generic index lookup, while directory filename lookup has its own direct filename collation path in `dir.c`.
