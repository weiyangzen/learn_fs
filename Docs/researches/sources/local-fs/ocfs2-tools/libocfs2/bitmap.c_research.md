# File Research: sources/local-fs/ocfs2-tools/libocfs2/bitmap.c

Implements the generic bitmap abstraction used by OCFS2 allocation code. A bitmap has total/set bit counts, operation hooks, an rb-tree of `ocfs2_bitmap_region` objects, and optional private data.

Public wrappers validate bit ranges and delegate to bitmap operations for set, clear, test, find-next-set, find-next-clear, allocate range, clear range, read, write, and free. They maintain the global set-bit count based on old bit values.

Region management supports allocation, reallocation, insertion into an rb-tree, lookup by intersecting bit range, iteration, and merging adjacent compatible regions. Merge handles byte-aligned and bit-shifted copies but refuses unaligned region starts and regions exceeding `INT_MAX`.

Generic operations require allocated memory for each bit; “holes” operations lazily allocate single-bit regions for sparse block bitmaps and treat missing regions as clear. Range allocation searches regions for a maximal clear run, falls back to the best run satisfying `min_len`, sets all chosen bits, and reports the first bit plus length found.

Factory APIs: `ocfs2_cluster_bitmap_new()` builds a full cluster bitmap split into `INT_MAX`-bounded regions; `ocfs2_block_bitmap_new()` builds a sparse block bitmap. `DEBUG_EXE` provides an interactive bitmap command shell.
