# File Research: sources/os/linux/linux/fs/xfs/scrub/attr.h

This header declares shared scratch storage and helpers for extended attribute scrub and repair. `struct xchk_xattr_buf` contains a used-space bitmap, a free-space bitmap, a salvaged-name buffer, and a value buffer with its current allocation size.

The declared functions are `xchk_xattr_set_map`, which marks byte ranges in a bitmap while detecting overlaps and out-of-bounds regions, and `xchk_setup_xattr_buf`, which allocates or resizes the reusable scrub/repair buffers. These declarations are used by both `attr.c` and `attr_repair.c` so that repair can reuse the same occupancy-map and value-buffer logic used by scrub validation.

The header is intentionally small and has no policy logic; it defines the common data contract for xattr metadata checking and salvage.
