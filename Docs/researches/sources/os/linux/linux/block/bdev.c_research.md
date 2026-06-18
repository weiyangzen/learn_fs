# File Research: sources/os/linux/linux/block/bdev.c

`bdev.c` implements Linux block-device inode objects, pseudo-filesystem backing, open/claim/release logic, cache invalidation, freeze/thaw, block-size management, lookup helpers, and statx support.

Block device object model:
- `struct bdev_inode` embeds `struct block_device` plus the VFS inode.
- `I_BDEV()` maps a block-device inode to `struct block_device`; `file_bdev()` maps an open block-device file to its bdev.
- The block device pseudo filesystem `bd_type` is mounted during `bdev_cache_init()`, and `blockdev_superblock` is exported for writeback.
- `bdev_alloc()` creates internal bdev inodes, initializes locks/counters/stats, sets the queue, and associates whole-disk or partition state.
- `bdev_add()`, `bdev_unhash()`, `bdev_drop()`, and `disk_live()` manage visibility and lifetime.

Cache and block size:
- `invalidate_bdev()` invalidates clean cached pages/buffers.
- `truncate_bdev_range()` drops cache for a byte range, temporarily claiming exclusivity when needed to avoid invalidating live filesystem buffers.
- `kill_bdev()` truncates all pagecache and buffer state.
- `sync_blockdev_nowait()`, `sync_blockdev()`, and `sync_blockdev_range()` flush block-device mappings.
- `set_blocksize()`, `sb_set_blocksize()`, and `sb_min_blocksize()` validate block sizes, flush/kill cached folios under inode and invalidation locks, and update mapping minimum folio order.
- Large block sizes require filesystem `FS_LBS` support and transparent hugepages.

Freeze/thaw:
- `bdev_freeze()` increments `bd_fsfreeze_count`, invokes holder `freeze` if present, otherwise syncs the block device.
- `bdev_thaw()` decrements the count and invokes holder `thaw` when the last freeze is released.
- `bd_fsfreeze_mutex` serializes freeze/thaw state.

Claim and exclusivity:
- Global `bdev_lock` serializes block-device holder state.
- `bd_prepare_to_claim()` waits for in-progress claims and rejects conflicting holders.
- `bd_finish_claiming()` records holder and holder ops, increments holder counters on whole and target bdev.
- `bd_abort_claiming()` cancels a prepared claim.
- `bd_end_claim()` releases holder state and unblocks disk events for write holders.
- Holder ops provide callbacks for freeze, thaw, and mark-dead.

Open/release:
- `bdev_permission()` checks device-cgroup permissions and validates write-restriction rules.
- `blkdev_get_no_open()` looks up an existing block-device inode by `dev_t`, optionally using deprecated legacy autoloading.
- `bdev_open()` handles exclusive claim setup, disk event blocking, module refcounting, live-disk checks, write policy checks, whole/partition open, write-access accounting, file setup, and error unwinding.
- `bdev_file_open_by_dev()` and `bdev_file_open_by_path()` allocate pseudo files and call `bdev_open()`.
- `bdev_release()` syncs if likely last opener, yields write access and holder claim, flushes media-change events, closes whole/partition references, drops the module, and releases the no-open reference.
- `bdev_fput()` synchronously yields claims before deferred `fput()`.

Mounted-device write policy:
- `bdev_allow_write_mounted` defaults from `CONFIG_BLK_DEV_WRITE_MOUNTED` and is controlled by `bdev_allow_write_mounted=`.
- If disabled, `bd_writers` tracks normal writers and write-restricting holders. Direct writes can be blocked while a restricting holder exists, and restricting holders are denied while writers exist.

Other services:
- `lookup_bdev()` resolves a path in the current namespace to a block-device `dev_t`.
- `bdev_mark_dead()` notifies holder ops or syncs, then invalidates cached data.
- `sync_bdevs()` iterates all block-device inodes and either starts or waits for writeback.
- `bdev_statx()` fills direct-I/O alignment and atomic-write statx fields by looking up the internal bdev from the device-node inode.
- `block_size()` returns the current internal inode block size.

Key dependencies include VFS inode/pagecache APIs, blkdev/gendisk APIs, device cgroups, security hooks, disk events, module refs, and filesystem holder callbacks.
