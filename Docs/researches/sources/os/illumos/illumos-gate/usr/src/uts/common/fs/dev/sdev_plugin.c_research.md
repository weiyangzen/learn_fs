# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_plugin.c

This file implements the dynamic directory plugin interface for sdev. It lets kernel subsystems register `/dev/<name>` dynamic directories backed by in-kernel state, instead of hard-coding all such directories in sdev itself.

Core concepts:
- A plugin provides `spo_validate`, `spo_filldir`, and `spo_inactive`.
- The plugin interface exposes context helpers for vnode type, path, name, minor number, and global flag.
- Plugins may create child directories and character/block nodes through `sdev_plugin_mkdir()` and `sdev_plugin_mknod()`.
- A global plugin list maps `/dev` paths to plugin vnode ops, flags, and validators.
- Legacy `vtab` dynamic directories are registered as legacy plugins.

Key routines:
- `sdev_plugin_register()` validates the name and ops, ensures a unique global `/dev` entry, inserts the plugin, and creates its top-level directory.
- `sdev_plugin_unregister()` removes the plugin, walks all sdev mounts to stale matching directories, waits for plugin node count to drain, then frees the plugin.
- `sdev_plugin_vop_lookup()` and `sdev_plugin_vop_readdir()` validate existing entries, call `spo_filldir()`, and delegate lookup/readdir formatting to common sdev helpers.
- `sdev_plugin_vop_inactive_cb()` calls `spo_inactive()` only when a node is truly zombie and decrements the plugin’s active node count.
- `sdev_get_vop()` selects plugin vnode ops and flags for a node based on its `/dev` path.
- `sdev_get_vtor()` returns either a legacy validator or the generic plugin validator.
- `sdev_plugin_nodeready()` attaches non-legacy plugin state to new nodes and increments node count.
- `sdev_plugin_init()` creates caches/locks, registers legacy vtab entries, and builds plugin vnode ops.

Lock ordering is explicitly documented: `sdev_plugin_lock` precedes per-plugin locks, and once plugin locks are held the code must not acquire sdev node holds or contents locks.

Risk areas:
- Plugin unregister is guarded by `sdev_plugin_unregister_allowed` because detach-context use can deadlock or return busy.
- `sdev_match()` path matching for `SDEV_SUBDIR` plugins is central to routing.
- Plugin callbacks execute with blocking allowed and with sdev contents locks held in the wrapper paths, so callback behavior must respect API restrictions.
