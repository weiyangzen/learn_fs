# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/bpobj.h

Read status: complete, 95 lines.

Purpose: defines persistent block-pointer object storage, typically used for deadlists and deferred frees.

Key structures and APIs:
- `bpobj_phys_t` is the bonus-buffer physical summary: number of block pointers, byte/compressed/uncompressed totals, and subobject counts.
- `bpobj_t` is the in-core opened object, with lock, objset/object id, entries-per-block, feature flags, physical pointer, and dbufs.
- Allocation/free/open/close APIs include `bpobj_alloc()`, `bpobj_alloc_empty()`, `bpobj_free()`, `bpobj_open()`, `bpobj_close()`.
- Iteration and enqueue APIs include `bpobj_iterate()`, `bpobj_iterate_nofree()`, `bpobj_enqueue()`, and `bpobj_enqueue_subobj()`.
- Space-query APIs include `bpobj_space()`, `bpobj_space_range()`, and `bpobj_is_empty()`.

Dependencies: DMU objects/transactions, SPA block pointers, TXG, ZIO, ZFS context.

Research notes:
- Supports older physical sizes (`BPOBJ_SIZE_V0`, `BPOBJ_SIZE_V1`) and optional compressed/subobject accounting.
- Forms a major building block for dataset deadlists and pool free/obsolete block tracking.
