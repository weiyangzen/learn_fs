# File Research: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_swap.h

This header provides endian conversion macros for Squashfs 4.0 disk structures. It is designed so little-endian hosts mostly copy or no-op, while big-endian hosts use byte-swap helpers from `swap.c`.

Key contents:
- Big-endian declarations for `swap_le16/32/64`, bulk swap helpers, and in-place swap helpers.
- `_SQUASHFS_SWAP_*` macros for superblock, directory indexes, inode variants, directory entries, fragment entries, and xattr structures.
- Public copy-swap macros such as `SQUASHFS_SWAP_SUPER_BLOCK`.
- Public in-place macros such as `SQUASHFS_INSWAP_SUPER_BLOCK`.
- Little-endian definitions that map copy operations to `memcpy` and in-place operations to no-ops.

Important behavior:
- Signed directory entry inode deltas are handled with `SWAP_LES`/`INSWAP_LES` to preserve sign.
- v4 `unsquash-4.c` reads disk data into native structs, then calls `SQUASHFS_INSWAP_*`; this header determines whether anything changes.
- Bulk table swaps cover fragment indexes, lookup blocks, id blocks, shorts, ints, and long longs.

Corruption-sensitive details:
- The macro field lists must match `squashfs_fs.h` exactly.
- The little-endian path intentionally does not validate values; callers perform sanity checks after in-place conversion.
