# File Research: sources/os/linux/linux/fs/jffs2/gc.c

This file implements JFFS2 garbage collection. A GC pass checks unchecked nodes, erases pending blocks, chooses a source eraseblock, moves or obsoletes one live node, and schedules fully obsolete blocks for erasure.

`jffs2_find_gc_block()` selects a block under `erase_completion_lock`, weighted by list and `jiffies`: bad-used when enough free blocks exist, then erasable, very-dirty, dirty, clean, and fallbacks. It also flushes pending writebuffer blocks when `erasable_pending_wbuf_list` is the only source. The chosen block becomes `c->gcblock`, with `gc_node` initialized to `first_node`.

`jffs2_garbage_collect_pass()` is the top-level state machine. It takes `alloc_sem`, first forces CRC checking of unchecked inodes by walking inocache buckets and calling `jffs2_do_crccheck_inode()`, then handles one pending erase if available. For a GC block, it skips obsolete refs, handles inode-less nodes by copying pristine unknown nodes or marking them obsolete, delegates xattr nodes to xattr GC helpers, and handles inode nodes according to inocache state. Absent pristine nodes can be copied intact under `INO_STATE_GC`; otherwise the inode is fetched and `jffs2_garbage_collect_live()` performs type-specific rewrite. If the GC block reaches zero used bytes, it is moved to `erase_pending_list`.

`jffs2_garbage_collect_live()` locks `f->sem`, verifies the node is still in the current GC block and not obsolete, then identifies whether the raw node is metadata, a data fragment, a live dirent, or a deletion dirent. Data fragments may use the pristine fast path, hole rewrite path, or page-based dnode rewrite path.

`jffs2_garbage_collect_pristine()` copies a raw pristine node byte-for-byte when it fits in newly reserved GC space and passes header/node/data/name CRC checks. If it cannot fit, or validation says the slow path is needed, it returns `-EBADFD`. On write failure it marks any partially written bytes obsolete and retries one allocation.

`jffs2_garbage_collect_metadata()` rewrites special metadata-only nodes, preserving device numbers or symlink targets, computing current inode length from the fragment tree when available, and replacing `f->metadata`.

`jffs2_garbage_collect_dirent()` writes a replacement dirent with a new version and reinserts it into the directory list. `jffs2_garbage_collect_deletion_dirent()` either preserves a deletion dirent on media where nodes cannot be permanently marked obsolete, if it still suppresses an older real dirent, or removes and obsoletes it.

`jffs2_garbage_collect_hole()` rewrites `JFFS2_COMPR_ZERO` hole nodes, preserving the old version for partially overlapped multi-fragment holes where possible. `jffs2_garbage_collect_dnode()` may expand the rewrite range to adjacent page fragments in dirty blocks, reads the folio with the correct folio-before-`f->sem` lock order, recompresses chunks through `jffs2_compress()`, writes replacement inode data nodes, and updates the fragment tree.

Key dependencies: eraseblock lists/accounting, inocache states, fragment tree logic, raw node writers, compression subsystem, page cache, xattr GC, CRC32, and MTD reads/writes.

Important invariants: `alloc_sem` serializes GC with allocation and many write paths; `INO_STATE_GC` prevents read_inode races for absent pristine nodes; GC must either increase dirty accounting or obsolete the target node, otherwise it reports `-ENOSPC`.
