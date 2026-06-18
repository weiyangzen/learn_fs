# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_ioctl.c

Implements the illumos ZFS `/dev/zfs` ioctl control plane and module driver entry points. It is the central kernel dispatcher for pool administration, dataset administration, send/receive, properties, delegation, snapshots/bookmarks/holds, encryption keys, sharing, fault injection, zvol forwarding, and control-device cleanup state.

Key elements:
- Defines the modern ioctl registration model with `zfs_ioc_vec_t`, `zfs_ioctl_register()`, per-command input-key schemas, name checking, pool-state checking, optional history logging, and output-nvlist smushing.
- Preserves legacy ioctl support through `zfs_ioc_legacy_func_t` handlers and registration helpers for pool, dataset read, dataset modify, and metadata commands.
- Provides broad security-policy functions for global-zone versus local-zone visibility, delegated dataset permissions, pool configuration privilege, share ACL checks, snapshot/bookmark/hold/release permissions, send/receive permissions, encryption key permissions, and labeled-system MLS label rules.
- Handles nvlist copyin/copyout with `get_nvlist()`, `put_nvlist()`, `nvlist_smush()`, and `zfs_check_input_nvpairs()`.
- Implements pool operations including create, destroy, import/export, tryimport, stats/config listing, scrub/scan, freeze, upgrade, reguid, sync, checkpoint/discard checkpoint, initialize, trim, wait, clear, and reopen.
- Implements vdev operations including add, remove/cancel remove, online/offline/fault/degrade, attach, detach, mirror split, set path, and set FRU.
- Implements dataset operations including create, clone, destroy, rename, rollback, promote, remap, object-to-path/stats, dataset/snapshot listing, properties, received properties, ZPL properties, delegated ACLs, quotas, userspace accounting upgrades, temporary snapshots, and diffs.
- Implements snapshot/bookmark/hold operations through `dsl_dataset_snapshot()`, destroy snapshot nvl handling, bookmark create/get/destroy, user holds, user releases, and cleanup-fd support through `zfs_onexit`.
- Implements send/receive entry points, including legacy and nvlist send APIs, send-space estimation, send progress, resumable receive, delayed receive properties, local property overrides, received-property clearing/restoration, hidden encryption args, and cleanup action handles.
- Implements encryption key ioctls for load, unload, and change-key using `dsl_crypto_params_create_nvlist()` and SPA keystore calls.
- Implements NFS/SMB sharing and SMB ACL resource-file management, dynamically resolving sharefs/NFS/SMB symbols.
- Defines `/dev/zfs` driver entry points, control-device clone-open minor allocation, control-device close cleanup, zvol delegation for non-control minors, and module `_init`, `_fini`, and `_info`.

Main dependencies and interactions:
- Bridges userland `zfs`, `zpool`, and `libzfs_core` requests to SPA, DSL, DMU, ZPL, zvol, ZIL, delegation, crypto, vdev, scan, trim, initialize, checkpoint, send/receive, bookmark, and user-hold subsystems.
- Uses `zfs_onexit.c` for per-control-device callbacks used by temporary holds and resumable receive state.
- Uses ZPL helpers from `zfs_vfsops`, `zfs_znode`, `zfs_dir`, `zfs_ctldir`, and `zvol` when operations affect mounted filesystems or zvol device minors.
- Uses nvlist contracts from `sys/zfs_ioctl.h`; new ioctls are expected to declare acceptable input keys and use `zfsdev_ioctl()` validation before handler dispatch.
- Uses `spa_history_log_nvl()` or legacy history strings to record state-changing operations when registration allows logging.
- Shares special property behavior with DSL/DMU/ZPL code: quotas and reservations go through DSL setters, volsize through zvol, ZPL version through mounted/unmounted zfsvfs handling, keylocation through crypto validation, and userquota through mounted zfsvfs quota routines.

Implementation notes:
- The file contains both old `zfs_cmd_t` field-based ioctls and newer nvlist-based ioctls. The top-level dispatcher enforces names, pool state, secpolicy, and input shape before invoking modern handlers.
- Pool-state checks reject operations on suspended pools with `EAGAIN` or readonly pools with `EROFS` according to command registration flags.
- Zone checks intentionally return `ENOENT` for datasets not visible in a local zone, avoiding information disclosure.
- Some property-setting operations are best effort: `zfs_set_prop_nvlist()` records per-property errors, retries selected failures, batches generic DSL property updates, and then falls back to individual sets.
- Receive property handling is failure-aware: it stashes original received/local props, clears old received props, extracts delayed properties such as `refquota` and `keylocation`, restores prior state on receive failure, and reports `ZPROP_ERR_*` flags when clearing/restoration cannot be guaranteed.
- Snapshot unmounting is best effort and forced for snapshot vfs instances; destroy, promote, rollback, and recursive snapshot rename paths use this to avoid mounted snapshot conflicts.
- The control device allocates clone minors for `O_EXCL` opens; these minors carry `zfs_onexit_t` lists and are destroyed on close, firing registered callbacks.
- The module initialization order is SPA, ZFS, zvol, ioctl registration, module install, TSD creation, LDI identity, and share lock setup; teardown refuses to unload when pools, ZFS mounts, zvols, or injection state are busy.

Risk/attention points:
- This file is an ABI and policy choke point. Adding or changing ioctls requires stable ioctl numbers, explicit nvlist key schemas, permission checks, pool-state flags, and history-log behavior.
- Legacy handlers can mutate `zc_name`, so `zfsdev_ioctl()` snapshots the pool name before dispatch for later history-log TSD use.
- Several code paths read objset contents without full ownership and document that as an existing compromise for stats/ZPL property access.
- Receive and property paths are particularly sensitive to partial failure: callers may observe both an errno and an output nvlist of per-property errors.
