# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/storage/slabhash.h

Defines the slabbed hash table interface.

Key structure:
- `struct slabhash`: number of slabs, high-bit mask, shift count, and array of `struct lruhash*`.

Public API:
- Lifecycle: `slabhash_create`, `slabhash_delete`, `slabhash_clear`.
- Dispatch operations: `slabhash_insert`, `slabhash_lookup`, `slabhash_remove`, `slabhash_update_space_used`, `slabhash_gettable`.
- Diagnostics and sizing: `slabhash_status`, `slabhash_get_size`, `slabhash_is_size`, `slabhash_get_mem`, `count_slabhash_entries`, `get_slabhash_stats`, `slabhash_adjust_size`.
- Traversal/control: `slabhash_setmarkdel`, `slabhash_traverse`.

Constants and test types:
- `HASH_DEFAULT_SLABS` defaults to 4.
- Test-only structures `slabhash_testkey` and `slabhash_testdata` are declared with helper callback prototypes.

Usage notes:
- Slab count must be a power of two.
- Each slab receives an equal share of the configured maximum memory.
