# File Research: sources/os/bsd/openbsd-src/sys/sys/blist.h

Purpose: Declares bitmap/radix-tree resource list structures and APIs, primarily for swap/block allocation style use.

Key contents:
- Defines `swblk_t`, `u_swblk_t`, and `SWAPBLK_NONE`.
- `blmeta_t` stores either available count or leaf bitmap plus biggest-contiguous-block hint.
- `struct blist` tracks total blocks, radix coverage, skip, free count, root metadata pointer, and root block allocation count.
- Defines metadata and bitmap radix constants, maximum block capacity, and maximum allocation size.
- Declares create, destroy, allocate, allocate-at, free, fill, print, resize, and gap-find operations.

Filesystem relevance:
- Useful for kernel block-resource allocation patterns adjacent to swap and storage management.
