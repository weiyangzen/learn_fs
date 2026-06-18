# File Research: sources/os/linux/linux/fs/gfs2/glops.c

## Scope

Defines glock operation callbacks for metadata, inode, resource group, freeze, iopen, flock, quota, journal, and nondisk glock types. Handles AIL flushing, metadata sync/invalidation, dinode refresh, freeze callbacks, and iopen eviction callbacks.

## Public And Internal APIs Covered

- Exported helpers: `gfs2_ail_flush()`, `gfs2_inode_metasync()`, `gfs2_glock2rgrp()`.
- Glock operation objects: `gfs2_meta_glops`, `gfs2_inode_glops`, `gfs2_rgrp_glops`, `gfs2_freeze_glops`, `gfs2_iopen_glops`, `gfs2_flock_glops`, `gfs2_nondisk_glops`, `gfs2_quota_glops`, `gfs2_journal_glops`, and `gfs2_glops_list[]`.
- Inode callbacks: `inode_go_sync()`, `inode_go_inval()`, `inode_go_instantiate()`, `inode_go_held()`, `inode_go_dump()`.
- Rgrp callbacks: `rgrp_go_sync()`, `rgrp_go_inval()`, `gfs2_rgrp_go_dump()`.
- Freeze/iopen callbacks: `freeze_go_callback()`, `freeze_go_xmote_bh()`, `iopen_go_callback()`.

## Control Flow And Behavior

- AIL flush walks a glock’s AIL buffers, adds revokes, withdraws on unexpected dirty/pinned/locked buffers outside fsync-tolerant paths, and flushes the log.
- Rgrp sync flushes the log for dirty rgrp glocks, writes/waits the metadata range, empties AIL state, and frees allocation clones.
- Rgrp invalidation releases rgrp buffers, asserts AIL is empty, and truncates the rgrp metadata range.
- Inode sync waits for direct I/O on regular files, unmaps shared writable mappings when needed, flushes metadata and data, empties AIL, clears dirty state, and wakes glop-pending waiters.
- Inode invalidation truncates metadata pages on full invalidation, marks instantiate needed, drops ACL/security/dir hash caches, invalidates rindex state, and truncates regular file page cache.
- Dinode refresh validates inode number, type, height, directory depth, exhash rules, stuffed-file size, and populates VFS inode metadata from disk.
- `inode_go_held()` waits for direct I/O for non-deferred holders and resumes interrupted truncation when the inode is held exclusive.
- Freeze callbacks schedule freeze work on remote unlock requests and reload journal-head state after freeze glock promotion/demotion.
- Iopen callback schedules remote eviction when another node wants the iopen glock unlocked.

## State And Invariants

- `GLF_DIRTY` controls whether inode/rgrp sync work is needed.
- `GIF_GLOP_PENDING` protects inode pointers during glock operation callbacks.
- Inode glocks use `GLOF_ASPACE | GLOF_LVB`; rgrp and quota glocks use LVBs.
- Metadata invalidation requires empty AIL state.
- Dinode validation defends against stale or corrupt on-disk metadata before exposing inode state.
