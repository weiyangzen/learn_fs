# File Research: sources/teaching/os161/kern/include/bitmap.h

Declares an opaque fixed-size bitmap abstraction intended for storage management.

Key APIs:
- `bitmap_create`, `bitmap_destroy`.
- `bitmap_getdata` exposes raw data for disk I/O.
- `bitmap_alloc` finds and sets a clear bit.
- `bitmap_mark`, `bitmap_unmark`, `bitmap_isset`.

Relevance:
- SFS freemap stores allocated blocks as set bits.
- `sfs_balloc`, `sfs_bfree`, and `sfs_bused` are thin filesystem-specific policy over this bitmap.
