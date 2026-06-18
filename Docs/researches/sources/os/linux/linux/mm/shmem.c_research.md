# File Research: sources/os/linux/linux/mm/shmem.c

Implements Linux shmem/tmpfs, the swap-backed in-memory filesystem used for tmpfs mounts, SysV/shared anonymous memory, `/dev/zero` shared mappings, memfd-style internal files, and many kernel users that need page-cache-backed volatile storage. The full implementation is enabled under `CONFIG_SHMEM`; without it, this file supplies a tiny ramfs-based tmpfs fallback plus the common shmem file setup helpers.

Key responsibilities:
- Maintains tmpfs superblock state, inode state, block/inode accounting, inode number allocation, quota integration, xattrs, ACLs, file attributes, casefolding, export handles, and mount/remount option parsing.
- Provides the core shmem page-cache API: `shmem_get_folio()`, `shmem_add_to_page_cache()`, swap entry replacement, swapin, swapout, truncate/hole-punch, fallocate, and read/write/splice paths.
- Implements tmpfs resource limits with per-superblock `used_blocks`, inode-space accounting, `SHMEM_F_NORESERVE` overcommit accounting, and optional in-memory dquot accounting.
- Supports tmpfs huge folios and transparent huge pages, including mount options, global/sysfs policy, mTHP order masks, huge-folio allocation fallback, end-of-file shrink handling, and a shrinker for unused large folio tails.
- Handles shmem swap lifecycle: page-cache entries can be real folios or encoded swap entries; `shmem_writeout()` replaces folios with swap entries, `shmem_swapin_folio()` moves data back, and `shmem_unuse()` scans all swapped shmem inodes during swapoff.
- Supplies VMA operations for ordinary tmpfs mappings and anonymous shmem mappings, including fault handling, NUMA shared mempolicy hooks, userfaultfd missing/minor support, and hugepage-friendly unmapped-area alignment.
- Implements tmpfs VFS operations: create, tmpfile, mkdir, link, unlink, rmdir, rename with whiteout/exchange support, symlink storage, statfs, getattr/setattr, fileattr get/set, xattr handlers, and export file handles.
- Registers and initializes the tmpfs filesystem, the internal kernel mount `shm_mnt`, tmpfs sysfs feature files, transparent hugepage sysfs controls, and boot parameters for shmem/tmpfs THP policy.
- Exports common helpers such as `shmem_file_setup()`, `shmem_kernel_file_setup()`, `shmem_file_setup_with_mnt()`, `shmem_zero_setup()`, `shmem_read_folio_gfp()`, and `shmem_read_mapping_page_gfp()`.

Important behavior:
- tmpfs file data is sparse and page-cache based. Holes read as zeroes, while allocated folios are charged incrementally unless the caller pre-accounted object size through shmem file setup.
- `info->alloced`, `info->swapped`, and `mapping->nrpages` are intentionally reconciled by `shmem_recalc_inode()` because the VM can drop clean hole pages or move folios between cache and swap behind VFS operations.
- Swap entries are stored in the mapping xarray as exceptional entries. Large folios and large swap entries require aligned index/order handling and can be split when swapin falls back to smaller folios.
- Swapoff uses a global `shmem_swaplist`; inode eviction coordinates with `stop_eviction` so the inode is not removed/freed while `shmem_unuse()` is scanning it.
- `shmem_writeout()` refuses swapout for locked shmem, noswap mounts, lack of swap, or fallocate races; otherwise it allocates swap, replaces the page-cache entry, submits swap I/O, and repairs state if writeout requests reactivation.
- `shmem_get_folio_gfp()` is the central lookup path. It handles cache hit, swapin, hole read, no-allocation lookup, userfaultfd interception, huge folio allocation, accounting failure cleanup, and truncate races.
- Hole punching uses `inode->i_private` as a temporary `struct shmem_falloc` rendezvous so page faults into the punched range wait instead of continuously refilling the hole.
- Fallocate can allocate not-yet-uptodate folios and roll them back if later allocation fails. `info->fallocend` protects fallocated large folio portions beyond `i_size` from being freed by truncation/splitting logic.
- Reads and splice reads treat absent folios as zeroes and fall back to base-page copying/splicing if a large folio has a hardware-poisoned subpage.
- `shmem_get_unmapped_area()` may inflate and adjust the chosen address so file offsets align with PMD-sized or mTHP-sized mappings when huge shmem is enabled.
- tmpfs remount can relax/tighten existing block and inode limits only if current usage fits; it cannot retroactively impose limits on unlimited mounts, cannot disable swap on remount, and cannot enable/change quotas after mount.
- Inode numbers can be 32-bit-compatible or full-width. Kernel-only mounts use per-CPU batched inode number allocation because those objects are created from contexts where the normal superblock stat lock is undesirable.
- Casefold support depends on Unicode support and only applies to directories; enabling/disabling it is rejected when the directory is non-empty.
- Security xattrs can be initialized during inode creation. tmpfs charges xattr storage against inode-space limits when inode limits are active.
- The tiny-shmem fallback registers tmpfs using ramfs operations and implements only no-op or ramfs-backed versions of the common shmem hooks.

Dependencies:
- Relies on the Linux VFS, page cache/xarray, swap subsystem, memcg charging, folios, LRU/writeback, rmap/MMU notifier side behavior through swap/page-cache helpers, inode/dentry helpers, quota core, xattr/simple_xattr, POSIX ACLs, fs_context parsing, mempolicy, userfaultfd, THP/mTHP helpers, sysfs/debug boot parameter infrastructure, security hooks, and ramfs fallback code.

Notable risks:
- The file has many cross-subsystem invariants: xarray entries, swapcache folios, `mapping->nrpages`, inode accounting, quota accounting, memcg charging, and folio lock state must be updated in the right order on every success and rollback path.
- Large folios increase boundary complexity: truncate, hole-punch, swapout, swapin, fallocate, EOF shrink, hardware poison, and hugepage policy all need consistent base-index/order calculations.
- Swapin/out races are expected. Correctness depends on repeated confirmation that the mapping still contains the expected swap entry and on converting `-EEXIST` races into retries.
- `inode->i_private` is reused for fallocate coordination rather than a permanent inode field; it is protected by inode locks/rwsem assumptions that must remain valid for all users.
- tmpfs quotas are volatile and in-memory; mount/remount restrictions protect against losing limits or enabling incomplete accounting after objects already exist.
