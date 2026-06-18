# File Research: sources/os/linux/linux-stable/fs/ocfs2/quota_local.c

Purpose: implements OCFS2 node-local quota files. These files store per-node quota deltas and use chunk bitmaps so quota state can be recovered after a node crash and folded into the global quota file.

Read coverage: complete file read, 1318 lines.

Key responsibilities:
- Defines local quota chunk/block/entry offset helpers for chunk headers and local dquot records.
- Validates local and global quota file format magic/version during quota enable.
- Loads local quota chunk bitmaps into memory and releases them on quota shutdown.
- Writes local quota info headers and local dquot delta records.
- Creates and releases per-node local dquot entries.
- Performs quota recovery for crashed slots.

Major logic:
- `ocfs2_modify_bh()` wraps a small journal transaction around a buffer-head mutation callback.
- `ocfs2_read_quota_block()` reads logical quota file blocks and validates quota ECC, refusing reads beyond file size as corruption.
- `ocfs2_begin_quota_recovery()` scans a crashed slot’s local quota files after journal replay and records chunks with allocated entries.
- `ocfs2_finish_quota_recovery()` locks the crashed local quota file, replays pending local deltas into global quota records with `ocfs2_recover_local_quota_file()`, then marks recovered files clean when appropriate.
- `ocfs2_local_read_info()` initializes `ocfs2_mem_dqinfo`, reads global and local quota headers, loads chunk bitmaps, queues self-recovery if the local file was dirty, and marks the local file in-use.
- `ocfs2_local_free_info()` checks that all local entries were freed, marks the file clean if safe, releases global lock resources, unlocks the local quota inode, and frees memory.

Allocation behavior:
- `ocfs2_find_free_entry()` searches loaded chunk bitmaps for a free local dquot slot.
- `ocfs2_local_quota_add_chunk()` extends an empty/full local quota file by adding a chunk header and first entry block.
- `ocfs2_extend_local_quota_file()` adds an entry block to the last chunk until the chunk is full, then creates a new chunk.
- `ocfs2_create_local_dquot()` allocates a bitmap slot, stores local file offset and physical block in `ocfs2_dquot`, writes the initial local delta record, and marks the slot allocated.
- `ocfs2_local_release_dquot()` clears the bitmap bit inside the caller’s already-started release transaction.

Important entry points:
- Format ops: `ocfs2_local_check_quota_file()`, `ocfs2_local_read_info()`, `ocfs2_local_free_info()`.
- Recovery: `ocfs2_begin_quota_recovery()`, `ocfs2_finish_quota_recovery()`, `ocfs2_free_quota_recovery()`.
- Local dquot I/O: `ocfs2_local_write_dquot()`, `ocfs2_create_local_dquot()`, `ocfs2_local_release_dquot()`.
- Exported quota format is `ocfs2_quota_format`.

Concurrency and dependencies:
- Local quota file allocation is serialized by the local quota inode’s `ip_alloc_sem`.
- Local dquot writes are serialized by quota core locks / `dqio_sem` and journaled through OCFS2 quota journal access.
- Recovery locks crashed slot local quota files with recovery or noqueue lock modes to avoid duplicate recovery.
- Depends on global quota helpers from `quota_global.c`, OCFS2 system files, inode locks, journaling, extent maps, and quota core APIs.

Risks and edge cases:
- Local quota files are intentionally dirty while mounted; clean marking is withheld if entries remain allocated or recovery was aborted.
- Recovery must drop the crashed node’s global use count while applying its local space/inode deltas.
- Chunk bitmap corruption can make free count and actual free bits disagree; this path reports errors and can return `-EIO`.
- Extending local quota files updates file size, chunk headers, info headers, and initialized entry blocks in carefully ordered transactions.
