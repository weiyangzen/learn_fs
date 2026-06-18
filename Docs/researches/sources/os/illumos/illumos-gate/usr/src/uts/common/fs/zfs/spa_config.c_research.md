# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/spa_config.c

This file manages cached pool configuration nvlists: loading cache files into the SPA namespace, writing cache files atomically, exposing all configs to zones, generating config nvlists, and syncing config changes.

Key behavior:
- `spa_config_load()` reads `spa_config_path` (`ZPOOL_CACHE` by default), unpacks an nvlist, and calls `spa_add()` for pools not already present in the namespace.
- `spa_config_write()` packs an nvlist and writes it via temp file, fsync, and rename; if passed `NULL`, it removes the cachefile.
- `spa_write_cachefile()` requires `spa_namespace_lock`, walks each cachefile path associated with the target pool, builds an nvlist of writeable pools using that cachefile, writes it, handles write failures with ereports and async retry, prunes old cachefile list entries, bumps `spa_config_generation`, and can post config sysevents.
- Readonly pools are intentionally skipped from cachefile writes because they may not be importable on reboot.
- Temporary-name imports use the previous pool name stored in `ZPOOL_CONFIG_POOL_NAME` rather than `spa_name()`.
- `spa_all_configs()` supports local-zone visibility by returning configs only for pools visible in the zone and only when `spa_config_generation` changed.
- `spa_config_set()` replaces the in-core `spa_config` under `spa_props_lock`.
- `spa_config_generate()` builds a pool or top-vdev config nvlist from in-core state, including version, name, state, txg, GUIDs, host identity, comments, top GUIDs, spare/log flags, per-vdev ZAP support, split metadata, vdev tree, read-required features, and optional DDT stats.
- `spa_config_update()` dirties labels or expands pending top-level vdevs, waits for the MOS config to sync, updates the global cachefile unless this is a root pool, and cascades pool updates into vdev updates.

Important invariants:
- Cachefile writes happen after MOS config sync, leaving a crash window where explicit import may be needed.
- `spa_config_generate()` takes `SCL_CONFIG | SCL_STATE` when it must lock itself.
- Config cache generation is a coarse change detector for consumers.
