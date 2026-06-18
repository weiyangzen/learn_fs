# File Research: sources/local-fs/squashfs-tools/squashfs-tools/xattr.c

Mksquashfs-side extended attribute collection, normalization, deduplication, encoding, and table writing.

Key responsibilities:
- Converts system, tar, pseudo, global `-xattrs-add`, and action-generated xattrs into Squashfs xattr IDs.
- Maintains compressed xattr metadata table, uncompressed staging cache, xattr id table, saved append state, duplicate-value hash table, duplicate-id hash table, and global xattr-add list.
- Determines xattr prefix/type using `prefix_table` and stores both full names and prefix-stripped names.
- Chooses inline vs out-of-line value storage. Values above `XATTR_INLINE_MAX` or lists exceeding `XATTR_TARGET_MAX` are pushed out-of-line more aggressively.
- Deduplicates whole xattr lists and individual large values via checksum/hash plus full comparison.
- Writes final compressed xattr metadata and xattr id table using `write_xattrs()`.
- Supports append mode by importing existing xattrs with `get_xattrs()`, and by `save_xattrs()`/`restore_xattrs()` on abort.
- Parses xattr literals for `xattrs-add` and pseudo/actions: raw/binary, `0s` base64, `0x` hex, and `0t` escaped text.
- Sorts and merges global, pseudo, and action xattr-add lists, rejecting duplicate final names.
- Filters invalid `user.*` xattrs on non-file/non-directory inode types.

Important exported functions include:
- `xattr_get_prefix()`, `read_xattrs()`, `get_xattrs()`, `write_xattrs()`, `save_xattrs()`, `restore_xattrs()`, `xattr_regex()`, `base64_decode()`, `xattr_parse()`, `xattrs_add()`, `sort_xattr_add_list()`, and `add_xattrs()`.

Dependencies:
- `mksquashfs` globals and helpers for compression, table output, checksums, pathname generation, and xattr action evaluation.
- `read_xattrs.c`, tar xattr support, pseudo/action modules, `virt_disk_pos`, and merge-sort macros.
