# File Research: sources/local-fs/ocfs2-tools/libocfs2/bitmap.h

Private bitmap header for libocfs2. It defines `struct ocfs2_bitmap_region`, `struct ocfs2_bitmap_operations`, and the internal `_ocfs2_bitmap`.

Regions track rb-tree linkage, starting bit, bitmap offset, valid/total bits, byte allocation, set-bit count, backing byte array, and private data. Operation hooks cover bit operations, lookup helpers, optional region merge, disk read/write, destroy notification, bit-change notification, range allocation, and range clearing.

The header declares generic bitmap construction and region APIs plus generic and holes-based operation implementations. It also defines the `ocfs2_bitmap_foreach_func` callback shape used by chain allocator writeback and lookup routines.
