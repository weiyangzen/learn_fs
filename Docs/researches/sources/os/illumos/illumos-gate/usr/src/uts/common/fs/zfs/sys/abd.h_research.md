# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/abd.h

This header declares the ABD abstraction, which represents ZFS buffers as either linear memory or scattered chunks and provides common allocation, ownership, copy, compare, zero, and RAID-Z iteration interfaces.

Key definitions:
- `abd_flags_t` includes `ABD_FLAG_LINEAR`, `ABD_FLAG_OWNER`, and `ABD_FLAG_META`.
- `abd_t` stores flags, logical size, optional parent pointer, child refcount, and either scatter metadata (`abd_offset`, `abd_chunk_size`, flexible `abd_chunks[]`) or a linear buffer pointer.
- `abd_iter_func_t` and `abd_iter_func2_t` define callback signatures for iterating over one or two ABDs.
- `zfs_abd_scatter_enabled` controls scatter allocation behavior externally.
- `abd_is_linear()` tests the linear flag.

Declared operations:
- Allocation/free: `abd_alloc()`, `abd_alloc_linear()`, `abd_alloc_for_io()`, `abd_alloc_sametype()`, `abd_free()`.
- Views/wrappers: `abd_get_offset()`, `abd_get_offset_size()`, `abd_get_from_buf()`, `abd_put()`.
- Buffer conversion/borrowing: `abd_to_buf()`, `abd_borrow_buf()`, `abd_borrow_buf_copy()`, return-copy variants, and ownership transfer/release.
- Data operations: `abd_iterate_func()`, `abd_iterate_func2()`, `abd_copy_off()`, copy to/from raw buffers, compare, and zero.
- RAID-Z support: `abd_raidz_gen_iterate()` and `abd_raidz_rec_iterate()` pass chunk arrays to parity generation/reconstruction callbacks.
- Inline zero-offset wrappers provide `abd_copy()`, `abd_copy_from_buf()`, `abd_copy_to_buf()`, `abd_cmp_buf()`, and `abd_zero()`.
- Lifecycle functions are `abd_init()` and `abd_fini()`.

Important invariants:
- `abd_size` excludes scatter offset.
- Ownership and parent/child refcounts allow sub-ABD views without losing lifetime tracking.
