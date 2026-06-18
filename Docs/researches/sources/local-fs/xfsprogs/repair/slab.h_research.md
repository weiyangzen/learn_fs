# File Research: sources/local-fs/xfsprogs/repair/slab.h

Public slab-array interface.

Defines opaque `struct xfs_slab` and `struct xfs_slab_cursor`, plus functions for:
- Allocation and free.
- Appending fixed-size items.
- Sorting with caller-provided comparator.
- Counting items.
- Cursor creation/destruction.
- Peeking, advancing, and popping items.

Used by rmap/refcount collection and bulkload rebuild paths to hold large temporary record streams.
