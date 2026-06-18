# sources/object-store/garage/src/block/manager.rs

Purpose: central local/remote block storage manager. It stores immutable block files, exchanges blocks over RPC, tracks local reference counts, schedules resync/repair/scrub workers, and exposes operational metrics.

Important APIs/types/functions: constants `INLINE_THRESHOLD`, `BLOCK_GC_DELAY`, `BlockRpc`, `BlockManager`, `BlockResyncErrorInfo`; constructor `new`; worker hooks `spawn_workers`, `register_bg_vars`; public operations `rpc_get_block_streaming`, `rpc_put_block`, `block_incref`, `block_decref`, `get_block_rc`, `list_resync_errors`, `send_scrub_command`; local operations `read_block`, `write_block`, `find_block`, `fix_block_location`, `delete_if_unneeded`; RPC handler implementation.

Control flow: initialization loads or creates `DataLayout`, validates markers, persists layout, opens `block_local_rc`, creates `BlockResyncManager`, RPC endpoint, RAM buffer semaphore, metrics, and scrub persister. Writes compress optionally, reserve buffer memory for remote sends, and call target storage nodes with quorum. Local writes lock one of 256 hash-sharded mutation mutexes, write a random temp file, optionally fsync file and directory, then atomically rename and clean old location/format. Reads search primary then secondary directories, enforce a read semaphore timeout, verify data, quarantine corrupt files as `.corrupted`, and enqueue resync. RPC get iterates read candidates with timeout fallback.

State and persistence: persistent state includes block files under data directories, `data_layout` metadata file, directory marker files, `block_local_rc`, resync queue/error DB trees, and scrub/resync worker configs. `BLOCK_GC_DELAY` delays physical deletion after RC reaches zero. `data_fsync` controls file and directory durability.

Dependencies and integration points: integrates `garage_db`, `garage_rpc` endpoint/strategy/quorum helpers, `garage_net` streams, `garage_util` config/persister/background/time/metrics/error/data, `DataLayout`, `BlockRc`, `BlockResyncManager`, repair workers, and OpenTelemetry. It is consumed by model tables and admin local APIs for block repair/info.

Risks: block durability depends on temp-write/rename/fsync correctness and the `data_fsync` configuration. Compression preference affects `find_block` ordering and existing file reuse. Corrupt compressed data is not decoded to a hash before accepting the header-level verification result. Background enqueue after transaction commit is spawned immediately by `block_incref/decref`, so process crashes can delay resync scheduling unless repaired later. Quorum and layout calculations are critical during cluster reconfiguration.

Test signals: no local unit tests; behavior is covered by broader Garage integration tests and operational repair/resync paths. High-value tests include interrupted write temp cleanup, compressed/plain migration, corrupt file quarantine, secondary-location rebalance, and RPC fallback behavior.
