# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_iter.c

This file implements private iteration helpers for the `zpool` command, covering sorted pool lists and recursive vdev traversal.

Pool list API:
- `pool_list_get(argc, argv, proplist, err)`: creates a `zpool_list_t`, opens requested pools or all pools, expands requested property lists, and stores handles in an AVL tree sorted by pool name.
- `pool_list_update(zlp)`: adds newly discovered pools only when the list was created without explicit arguments.
- `pool_list_iter(zlp, unavail, func, data)`: invokes a callback for each pool, optionally including unavailable pools.
- `pool_list_remove(zlp, zhp)`: removes and closes a pool handle from the list.
- `pool_list_free(zlp)`: robust-walks the AVL tree, closes all pool handles, frees nodes, and destroys pools.
- `pool_list_count(zlp)`: returns the number of tracked pools.
- `for_each_pool(...)`: high-level wrapper used by ordinary subcommands.

Pool gathering behavior:
- With no arguments, `zpool_iter()` is used to add every pool and `zl_findall` is set so future updates can discover new pools.
- With explicit arguments, each pool is opened by `zpool_open_canfail()`, and the list remains fixed.
- Duplicate pool names are rejected by AVL lookup; duplicate handles are closed.
- Property expansion uses `zpool_expand_proplist()` when the caller supplies a property list pointer.

Vdev traversal:
- `for_each_vdev(zhp, func, data)` obtains the pool config, extracts `ZPOOL_CONFIG_VDEV_TREE`, and recurses through vdev nvlists.
- The recursion descends through `spares`, `l2cache`, and `children` arrays.
- Hole vdevs marked with `ZPOOL_CONFIG_IS_HOLE` are skipped.
- The callback is invoked for every non-root vdev after its children have been processed.

State and ownership:
- `zpool_list_t` owns its AVL tree, AVL pool, and retained `zpool_handle_t *` values.
- `add_pool()` transfers ownership of a successfully inserted handle to the list; on failure it closes the handle.
- `pool_list_iter()` does not remove or close handles; cleanup is explicit through `pool_list_free()` or `pool_list_remove()`.

Risk notes:
- `pool_list_update()` only works for all-pool lists; explicit lists intentionally do not grow.
- `pool_list_iter()` caches `next_node` before invoking callbacks, allowing callbacks to remove the current pool safely.
- Vdev traversal assumes the pool config contains `ZPOOL_CONFIG_VDEV_TREE`; the code verifies lookup success after a non-NULL config.
- The vdev callback order is post-order, not pre-order, which matters for consumers that aggregate or mutate vdev state.
