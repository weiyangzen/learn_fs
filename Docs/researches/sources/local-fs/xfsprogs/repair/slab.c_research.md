# File Research: sources/local-fs/xfsprogs/repair/slab.c

Implements a grow-only slab array with cursor iteration and optional sorted merge traversal.

Key structures:
- `struct xfs_slab_hdr`: one slab segment with item capacity, used count, and next pointer.
- `struct xfs_slab`: logical collection of increasingly sized slab segments.
- `struct xfs_slab_cursor`: per-slab cursors used to iterate either insertion order or sorted order across independently sorted slabs.

Core API:
- `init_slab` and `free_slab` create/destroy slab arrays.
- `slab_add` appends one fixed-size item, allocating larger segments as needed.
- `qsort_slab` sorts each slab segment, parallelizing with workqueue if there are more than four slabs.
- `init_slab_cursor`, `peek_slab_cursor`, `advance_slab_cursor`, and `pop_slab_cursor` iterate data.
- `slab_count` returns total items.

Important behavior:
- No random access or deletion is supported.
- Pointers are not stable across sort operations.
- Sorted cursor traversal performs a k-way merge over individually sorted slab segments.
- Slabs start with at least 4096 items and cap individual slab allocation at 128 MiB.
