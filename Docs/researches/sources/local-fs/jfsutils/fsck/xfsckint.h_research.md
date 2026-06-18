# File Research: sources/local-fs/jfsutils/fsck/xfsckint.h

Internal fsck interface header that gathers globals and cross-module function prototypes for `fsck.jfs`.

Key contents:
- Includes `xfsck.h`, message, workspace, physical filesystem, and endian headers.
- Declares device globals provided by `xchkdsk.c`: `Dev_IOPort`, block/sector sizes, and journal byte offset.
- Groups prototypes by implementation module:
  - Directory index/table verification.
  - Block allocation map verify/rebuild.
  - Connectivity, parent, directory integrity, and link-count checks.
  - Directory entry insert/delete/search/rebuild routines.
  - Aggregate and fileset inode map verification/rebuild.
  - Inode validation, EA/ACL backout/clear/validate, path display, release, and record/unrecord flows.
  - Metadata/superblock validation and replication.
  - Physical I/O accessors for inodes, iags, block-map pages, dnodes, xnodes, fscklog, and device open/close.
  - Heartbeat start/stop.
  - Workspace allocation, block ownership accounting, extent record/unrecord, queue helpers, temp buffers, fsck log lifecycle, and cleanup.
  - Xtree traversal/search/processing.
- Defines `inode_type_recognized()` macro over JFS inode mode type bits.

Interactions:
- This file is the main internal call graph surface across fsck modules.
- It exposes low-level I/O entrypoints also mirrored in `fscklog/extract.c`, which comments that duplicated routines should eventually move into `libfs`.

Research notes:
- Strongly procedural, global-state-based design.
- Provides high coupling between fsck subsystems; useful for mapping fsck module boundaries.
