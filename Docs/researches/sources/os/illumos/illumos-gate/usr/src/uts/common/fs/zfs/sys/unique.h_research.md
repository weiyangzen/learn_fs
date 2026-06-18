# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/unique.h

This header declares a small unique-value allocator used by ZFS code needing non-colliding 56-bit identifiers.

Core definitions:
- `UNIQUE_BITS` is 56 significant bits per unique value.

Public API surface:
- `unique_init()` / `unique_fini()` initialize and tear down global state.
- `unique_create()` returns a new candidate value that is not made collision-reserved until insertion.
- `unique_insert()` returns a unique value equal to the requested value if possible.
- `unique_remove()` releases a value from future uniqueness checks.

Risk-sensitive invariants:
- Creation and insertion are distinct; callers that need reservation must insert.
- Values outside the significant-bit model should not be assumed preserved.
