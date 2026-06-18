# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_util.h

## Purpose
Shared header for the illumos `zpool` command implementation. It declares utility helpers, vdev construction/splitting helpers, pool/vdev iteration APIs, pool-list management APIs, and the global libzfs handle.

## Main Elements
- Utility declarations: `safe_malloc()`, `zpool_no_memory()`, `num_logs()`, `array64_max()`, `highbit64()`, `lowbit64()`, and `isnumber()`.
- Vdev construction: `make_root_vdev()` and `split_mirror_vdev()`.
- Pool iteration: `for_each_pool()`.
- Vdev iteration: `pool_vdev_iter_f` and `for_each_vdev()`.
- Pool-list abstraction: `zpool_list_t`, `pool_list_get()`, `pool_list_update()`, `pool_list_iter()`, `pool_list_free()`, `pool_list_count()`, and `pool_list_remove()`.
- Global state: `extern libzfs_handle_t *g_zfs`.

## Dependencies And Integration
- Includes `<libnvpair.h>` and `<libzfs.h>`.
- Provides the shared contract between `zpool_main.c` and companion zpool modules for vdev parsing and pool iteration/list management.
- Exposes bit helper prototypes used by iostat flag handling.

## Risk Notes
- `g_zfs` is process-global and assumes initialization/teardown in `main()`.
- Several APIs accept mutable argv/property nvlist inputs, so ownership and mutation behavior must remain consistent.
- Some standard types rely on included lib headers or prior include order.
