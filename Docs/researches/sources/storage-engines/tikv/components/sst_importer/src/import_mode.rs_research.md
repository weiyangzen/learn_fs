# sources/storage-engines/tikv/components/sst_importer/src/import_mode.rs

Purpose: switches the whole RocksDB instance between normal mode and importer-optimized mode, then automatically restores normal mode after a timeout.

Important APIs and types: `ImportModeSwitcher` wraps `ImportModeSwitcherInner` and an atomic `is_import`. Public methods are `new`, `start_resizable_threads`, `enter_normal_mode`, `enter_import_mode`, and `get_mode`. `ImportModeDbOptions` stores `max_background_jobs`; `ImportModeCfOptions` stores L0 stop/slowdown triggers and pending-compaction limits. `RocksDbMetricsFn` reports option values.

Control flow: entering import mode snapshots current DB/CF options, sets DB `max_background_jobs` to at least 32, sets CF L0 stop/slowdown triggers to at least `1 << 30`, and disables soft/hard pending compaction byte limits. Entering normal mode restores all saved options. The background timer checks `next_check`; if timeout has elapsed and import mode is still active, it restores normal mode and schedules the next check. Each explicit `enter_import_mode` refreshes timeout and metrics function.

State and persistence behavior: mutates live RocksDB options and stores backups in memory. No on-disk metadata records the prior mode, so process restart relies on Rocks/default config rather than switcher memory.

Dependencies and integration points: used by `SstImporter` to reduce write stalls during bulk import. Depends on `KvEngine` option traits, global timer, resizable runtime handle, import config, and import protobuf `SwitchMode`.

Risks: correctness depends on capturing options before the first import-mode transition and restoring them exactly. `ImportModeCfOptions::new_options` unwraps CF option access. If the process exits while in import mode, in-memory backup is lost. The timer loop uses a weak reference and exits when switcher drops.

Test signals: tests verify option transitions, idempotent enter/exit, automatic timeout restoration, and that import mode does not reduce an already-high L0 stop writes trigger.
