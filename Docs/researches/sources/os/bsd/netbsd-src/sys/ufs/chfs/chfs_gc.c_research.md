# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_gc.c

Purpose: Implements CHFS garbage collection: background wakeup policy, candidate eraseblock selection, unchecked-node validation, and copying live nodes out of dirty blocks.

Main entry points:
- `chfs_gc_trigger`: signals the GC thread when thresholds say it should run.
- `chfs_gc_thread`, `chfs_gc_thread_start`, `chfs_gc_thread_stop`: manage the kernel GC thread.
- `chfs_gc_thread_should_wake`: wakes on erase-pending blocks, unchecked data, low free/erasable reserve, or too many very-dirty blocks.
- `chfs_gcollect_pass`: main GC pass.
- `find_gc_block`: chooses a block from erase-pending, very-dirty, dirty, or clean queues with weighted randomness.
- `chfs_gcollect_pristine`, `chfs_gcollect_live`, `chfs_gcollect_vnode`, `chfs_gcollect_dirent`, `chfs_gcollect_deletion_dirent`, `chfs_gcollect_dnode`: per-node relocation paths.

Important behavior:
- GC first resolves unchecked vnode caches by calling `chfs_check`, which builds a minimal inode and runs `chfs_read_inode_internal`.
- Candidate block selection avoids `chm_nextblock` and sets `chm_gcblock`.
- Fully dirty/wasted GC blocks are moved to `chm_erase_pending_queue` and remapped.
- Live vnode metadata is rewritten using `chfs_write_flash_vnode(..., ALLOC_GC)`.
- Live dirents are removed/obsoleted from old chains and rewritten with `ALLOC_GC`.
- Live data nodes are read, version-bumped, rewritten, then added back to the inode frag tree and vnode-cache data-node list.
- Pristine nodes are copied as raw node bytes after header/node CRC validation.

Dependencies:
- Relies on vnode cache states from CHFS core headers: `UNCHECKED`, `CHECKING`, `READING`, `PRESENT`, `GC`, `CHECKEDABSENT`.
- Uses `chfs_read_inode_internal` and fragment helpers from `chfs_readinode.c`.
- Uses write paths from `chfs_write.c`, queue/remap logic from `chfs_erase.c`, and node-list helpers from `chfs_nodeops.c`.

Research notes:
- Several code paths intentionally sleep/retry on concurrent vnode reading/checking.
- Some comments question current design, especially sleeps and GC state handling.
- `chfs_gc_release_inode` is a stub.
- The GC thread panics if GC cannot make space in a critical ENOSPC condition.
