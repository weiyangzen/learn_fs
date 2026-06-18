# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/unique.c

Implements a process-wide unique 64-bit value allocator backed by an AVL tree and random generation.

Key elements:
- Static `unique_avl` tracks allocated values.
- Static `unique_mtx` serializes tree access.
- `unique_t` stores AVL linkage and value.
- `UNIQUE_MASK` limits generated values to `UNIQUE_BITS`.
- `unique_init()` creates the AVL tree and mutex.
- `unique_fini()` destroys them.
- `unique_create()` obtains a unique value through `unique_insert(0)` and immediately removes it, returning a currently-unused random value.
- `unique_insert()` accepts a requested value or generates random values until nonzero, within mask, and absent from the AVL tree.
- `unique_remove()` removes a value if present.

Main dependencies and interactions:
- Includes ZFS context, AVL, and `sys/unique.h`.
- Uses `TREE_CMP()` from `zfs_context.h` and `random_get_pseudo_bytes()`.

Implementation notes:
- `unique_insert()` drops the mutex while generating random bytes, then reacquires and retries validation.
- Values are tracked only while inserted; `unique_create()` returns an unreserved value by design.
