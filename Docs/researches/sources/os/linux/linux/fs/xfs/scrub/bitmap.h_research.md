# File Research: sources/os/linux/linux/fs/xfs/scrub/bitmap.h

This header declares the sparse bitmap API implemented in `bitmap.c`. It defines `struct xbitmap64` and `struct xbitmap32`, each wrapping an `rb_root_cached`, and declares the complete operation set for both width variants.

For both 64-bit and 32-bit bitmaps the API includes `init`, `destroy`, `clear`, `set`, `disunion`, `hweight`, `walk`, `empty`, and `test`. The walk callback types are documented to return zero to continue and nonzero to stop, with `-ECANCELED` available as a caller-defined early-stop value. `xbitmap32_count_set_regions` is additionally exposed for callers that need extent-count rather than bit-count information.

This API is the generic base for typed wrappers such as AG block, filesystem block, and AG inode bitmaps. Its callers in scrub repair rely on sparse extent operations, especially subtraction and walking, to identify old metadata blocks and to replay or reap ranges.
