# File Research: sources/os/linux/linux/fs/jffs2/write.c

## Role

Implements core JFFS2 write-side node creation for inode data, metadata, directory entries, create, unlink, and link operations.

## Key Responsibilities

- `jffs2_do_new_inode()` allocates an inode cache, initializes present inode state, assigns an inode number, and initializes a raw inode header/version.
- `jffs2_write_dnode()` writes raw inode nodes and optional data payloads, retries failed writes when allowed, marks partial failed writes obsolete, creates a `jffs2_full_dnode`, and links the physical node ref.
- `jffs2_write_dirent()` writes raw dirent nodes, validates names do not contain embedded NUL bytes, retries failed writes, creates `jffs2_full_dirent`, and links the physical node ref.
- `jffs2_write_inode_range()` splits logical writes by page boundary and available allocation, compresses data, builds raw inode CRCs, writes dnodes, inserts them into the inode fragment tree, and obsoletes old metadata.
- `jffs2_do_create()` writes initial metadata node, initializes security and ACL metadata, writes the parent dirent, and links it into the parent directory list.
- `jffs2_do_unlink()` either writes a deletion dirent when physical obsoletion is unavailable or marks an existing dirent obsolete when it is available, then adjusts dead inode link/parent state.
- `jffs2_do_link()` writes a new dirent for hard links or directory operations and inserts it into the directory list.

## Important Interactions

- Uses reservation APIs from `nodemgmt.c` and must call `jffs2_complete_reservation()` after successful or failed allocations.
- Uses compression dispatcher from `compr.c`.
- Uses `jffs2_flash_writev()` so writes may be direct or write-buffered.
- Updates in-memory fragment and dirent trees via nodelist helpers.
- Calls security and ACL initialization during create.

## Invariants and Risks

- Raw node header CRC, node CRC, data CRC, and name CRC are built before writes and later trusted by scan/read paths.
- Non-GC writes may update versions on retry if another writer advanced `highest_version`.
- Failed writes with nonzero `retlen` are deliberately marked obsolete over the intended padded node length.
- Unlink behavior differs sharply depending on whether the medium can physically mark nodes obsolete.
