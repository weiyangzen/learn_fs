# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/swapfs/swap_subr.c

Swapfs initialization and shared support code for memory-backed swap vnodes, async putpage request queues, and dynamic recalculation of swapfs reserve thresholds.

Key responsibilities:
- Defines global swapfs reserve tunables/state: `swapfs_desfree`, `swapfs_minfree`, and `swapfs_reserve`.
- Initializes swapfs in `swapinit()`: mutexes, vnode table, reserve thresholds, memory-configuration callbacks, async request pool, VFS ops, and vnode ops.
- Creates per-identifier swap vnodes lazily in `swapfs_getvp()`, setting `VISSWAP` and `VISSWAPFS`.
- Implements `swap_sync()` to push pages from all swap vnodes on `SYNC_ALL`.
- Manages async request queues used by `swap_vnops.c`: pending list and free list through `sw_getreq`, `sw_putreq`, `sw_putbackreq`, `sw_getfree`, and `sw_putfree`.
- Recalculates reserve values in response to memory hotplug through `swap_mem_config_post_add`, `swap_mem_config_pre_del`, and `swap_mem_config_post_del`.

Dependencies:
- Uses `swap_vnodeops_template` from `swap_vnops.c`.
- Uses VM memory accounting globals such as `physmem`, `availrmem`, and `segspt_minfree`.
- Uses physical-memory configuration callback API `kphysm_setup_func_register`.
- Uses async request structures from swapnode/swap headers.

Concurrency and locking:
- `swapfs_lock` protects the vnode table, vnode count, and async request lists.
- Memory-delete callbacks use `swapfs_pending_delete` with atomic updates before recalculating viable thresholds.
- Async request insertion holds the vnode, and free-list return releases it.

Notable risks:
- `swapfs_recalc()` refuses memory-delete operations that would leave swapfs thresholds unsafe, returning `EBUSY`.
- `swapfs_getvp()` assumes `vidx` is within `MAX_SWAP_VNODES`; callers must enforce bounds.
- Async request pool size is tied to `klustsize / PAGESIZE * 2`; pressure behavior depends on that small fixed pool.
