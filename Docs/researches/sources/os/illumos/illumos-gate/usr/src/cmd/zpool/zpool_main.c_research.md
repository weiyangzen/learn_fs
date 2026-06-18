# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zpool/zpool_main.c

## Purpose
Primary implementation of the illumos `zpool` command-line utility. It parses subcommands and options, translates CLI requests into libzfs/libzutil operations, renders pool/vdev status and statistics, and records successful administrative actions in ZFS history.

## Main Elements
- Global CLI dispatch: command table, usage text, `main()`, libzfs initialization, history capture, `property=value` shorthand, and debug `freeze`.
- Property/vdev helpers: property nvlist validation, feature/version exclusion, vdev-tree traversal, dry-run output, and leaf collection.
- Pool creation/topology mutation: create/add/remove/attach/replace/detach/split/labelclear flows.
- Import/export/destroy/checkpoint/sync: discovery, duplicate-name handling, rewind/checkpoint policies, MMP/hostid safety, dataset mount/disable, and sync.
- Monitoring/reporting: list, status, iostat, timestamps, scripted/parsable modes, latency/queue/histogram stats, scan/removal/checkpoint progress, error logs, and dedup stats.
- Device maintenance: online/offline/clear/reguid/reopen/scrub/resilver/trim/initialize/wait.
- Upgrade/history/get/set: feature listing/enabling, pool version upgrades, paged history output, and pool property access.

## Dependencies And Integration
- Depends heavily on libzfs/libzutil for real pool, vdev, property, history, import/export, scan, wait, and dataset operations.
- Uses `zpool_util.h` plus companion zpool modules for `make_root_vdev()`, `split_mirror_vdev()`, `for_each_pool()`, `for_each_vdev()`, and `pool_list_*()`.
- Uses nvlists as the main interchange format for pool configs, vdev trees, stats, load policies, and properties.
- Uses ZFS structures/constants such as `vdev_stat_t`, scan/removal/checkpoint stats, DDT stats, and `spa_feature_table`.

## Notable Behaviors
- Rejects dataset-like pool names containing `/` for many pool-only commands.
- `zpool create` enables all supported feature flags unless disabled or an older version is requested.
- `-R` and temporary-name flows default `cachefile=none`.
- `zpool iostat -g` avoids misparsing numeric vdev GUIDs as interval/count.
- Status output separates normal, dedup, special, log, cache, and spare vdev classes.
- `zpool wait` can continue waiting for selected activities that begin while it is running.

## Risk Notes
- Very large CLI surface; option parsing and output formatting are externally observable compatibility contracts.
- Script-facing modes (`-H`, `-p`, `-T`, list/status/iostat columns) are sensitive to spacing and field order.
- Many nvlist accesses use `verify()`/`fnvlist_lookup_*()`, assuming kernel/libzfs invariants.
- `labelclear` directly opens and clears device labels, so force and membership checks are safety-critical.
- Several property parsers mutate `optarg` by replacing `=` with NUL.
- `wait_status_thread()` combines global libzfs state, pthreads, semaphore timing, and refresh/error handling.
- Debug `freeze` copies into a fixed buffer and is intentionally treated as a debugging-only path.
