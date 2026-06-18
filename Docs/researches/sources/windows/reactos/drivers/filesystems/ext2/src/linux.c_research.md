# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/linux.c

## Scope
Provides a Windows/ReactOS compatibility layer for Linux-style JBD and ext2 helper code, including slab-like caches, waitqueues, buffer heads, block-device buffer lookup, cache-manager-backed block reads/writes, block mapping, inode references, and compatibility initialization.

## Key Elements
- Defines a global `current_task` and `current` pointer for Linux-style current-task access.
- Implements `kzalloc()`, `kmem_cache_create()`, `kmem_cache_destroy()`, `kmem_cache_alloc()`, and `kmem_cache_free()` using nonpaged lookaside lists.
- Implements waitqueue initialization, add/remove, prepare/finish wait, and a stubbed `wake_up()`.
- Creates a buffer-head cache with `ext2_init_bh()` and `ext2_destroy_bh()`.
- `new_buffer_head()` and `free_buffer_head()` allocate/free buffer heads, MDLs, pinned BCBs, and memory accounting.
- Maintains buffer heads in a per-block-device red-black tree keyed by block number.
- `get_block_bh_pin()` and `submit_bh_pin()` use `CcPinRead()`, `CcPreparePinWrite()`, `CcSetDirtyPinnedData()`, and BCB ownership to back Linux buffer heads with Windows cache-manager pinned data.
- MDL-backed alternatives exist in `get_block_bh_mdl()` and `submit_bh_mdl()`, but the active build selects the pinned path.
- `__getblk()`, `__brelse()`, `__bforget()`, `ll_rw_block()`, `bh_submit_read()`, `sync_dirty_buffer()`, `mark_buffer_dirty()`, and `sync_blockdev()` supply JBD buffer IO semantics.
- `bmap()` maps inode logical blocks through `Ext2BuildExtents()`.
- `iget()` and `iput()` provide simple inode reference counting.
- `ext2_init_linux()` and `ext2_destroy_linux()` initialize/destroy buffer-head support.

## Dependencies
Depends on Ext2 VCB/block-device structures, Windows cache-manager APIs, MDL helpers, red-black tree helpers, buffer state macros, global BH reaper signaling, Ext2 extent mapping, and Ext2 flush/block-extent accounting.

## Behavior/Risks
- `wake_up()` is effectively a no-op, which limits fidelity for Linux waitqueue users unless higher-level code avoids relying on real wakeups.
- Buffer locks and waits are mostly stubbed, so correctness relies on surrounding Windows resources and cache-manager synchronization.
- `__find_get_block()` calls `__getblk()`, so it may instantiate a buffer rather than only finding an existing cached one.
- `__brelse()` writes dirty buffers before dropping references and queues zero-reference buffers to the VCB free list for the BH reaper.
- The active pinned-buffer path keeps cache-manager BCBs owned by the buffer head and marks pinned data dirty on write submission.
