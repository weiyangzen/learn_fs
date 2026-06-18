# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_misc.c

This broad infrastructure file implements SPA global state, locking, namespace lifecycle, vdev operation locking, auxiliary device tracking, tunables, accessors, import progress, scan stats, and initialization/finalization.

Key behavior:
- The opening block documents SPA lock ordering: `spa_namespace_lock`, per-SPA refcount, and ordered `spa_config_lock[]` levels from `SCL_CONFIG` through `SCL_VDEV`.
- Global tunables include debug flags, recovery behavior, deadman timing, free-on-EIO behavior, allocation inflation, slop-space policy, allocator count, special-class policy, and FPU enablement.
- `spa_load_failed()` and `spa_load_note()` emit structured debug messages for import/load diagnostics.
- `spa_config_lock_init()`, `spa_config_tryenter()`, `spa_config_enter()`, `spa_config_exit()`, and `spa_config_held()` implement multi-lock reader/writer config locking with writer ownership and waiters.
- Namespace functions include `spa_lookup()`, `spa_add()`, `spa_remove()`, and `spa_next()`, all coordinated by `spa_namespace_lock`.
- `spa_add()` allocates and initializes a `spa_t`, including mutexes, CVs, bplists, deadman cyclic, refcount, config locks, allocation trees, log-spacemap AVL/list structures, cachefile list, load info, label features, kstats, feature refcount cache, and leaf list.
- `spa_remove()` tears all of that down after the pool is uninitialized and refcount is zero.
- Refcount helpers are `spa_open_ref()`, `spa_close()`, `spa_async_close()`, and `spa_refcount_zero()`.
- Shared auxiliary AVL logic supports spares and L2ARC devices through `spa_aux_*`, with wrappers `spa_spare_*` and `spa_l2cache_*`.
- `spa_spare_poll()` probes inactive spares by scheduling async probe work.
- Vdev locking helpers `spa_vdev_enter()`, `spa_vdev_config_enter()`, `spa_vdev_config_exit()`, `spa_vdev_exit()`, `spa_vdev_state_enter()`, and `spa_vdev_state_exit()` coordinate namespace/config locks, autotrim, config sync, DTL reassessment, vdev free, state sync, and cachefile update.
- Miscellaneous helpers handle MOS feature activation, lookup by pool/device GUID, string allocation, random GUID generation, block-pointer formatting, pool freeze, recoverable panic behavior, hex parsing, and allocation-class feature activation.
- Accessors expose core SPA state, TXGs, root block pointer, dspace/checkpoint space, failmode, suspension, version, metaslab classes, log state, writeability, bootfs, delegation, MOS object set, dedup checksum, autotrim, multihost, and checkpoint predicates.
- `spa_preferred_class()` selects normal, log, special, or dedup allocation classes based on object type, level, size, and special-class reserve.
- Evicting objset helpers let unload wait for pending objset eviction and DMU buffer-user eviction.
- Size helpers compute DVA/BP disk size with deflation under `SCL_VDEV`.
- illumos import progress is exposed via kstats, with setters for load state, max TXG, and MMP seconds remaining.
- `spa_init()` initializes global AVL trees and subsystem dependencies; `spa_fini()` stops L2ARC, evicts pools, finalizes subsystems, and destroys globals.
- Scan helpers initialize and report pool scan stats, combining on-disk scan state with per-pass volatile counters.
- Checkpoint helpers include `spa_top_vdevs_spacemap_addressable()`, `spa_has_checkpoint()`, `spa_importing_readonly_checkpoint()`, `spa_min_claim_txg()`, and `spa_suspend_async_destroy()`.
- `zfs_post_dle_sysevent()` emits device LUN expansion sysevents in kernel builds.

Important invariants:
- Namespace mutation requires `spa_namespace_lock`.
- Vdev config changes are synchronized so administrator-visible operations wait for relevant TXGs.
- `spa_writeable()` requires both `FWRITE` mode and trusted config.
