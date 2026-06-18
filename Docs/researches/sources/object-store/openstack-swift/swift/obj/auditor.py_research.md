# sources/object-store/openstack-swift/swift/obj/auditor.py

## Purpose
`auditor.py` implements Swift's object-auditor daemon. It walks object hash directories for every configured storage policy, opens each object through the policy-specific diskfile manager, validates object metadata and content, quarantines corrupt objects, removes stale rsync temp files, writes recon metrics, and optionally invokes object audit watcher plugins.

The file is the runtime bridge between low-level object storage in `swift.obj.diskfile` and operator-facing daemon behavior: throttling, process fan-out, progress logging, recon cache reporting, and plugin hooks.

## Important APIs, Types, And Functions
`AuditorWorker` performs the actual scan. Its constructor reads rate limits, object-size-stat buckets, watcher definitions, a `DiskFileRouter`, and a conservative `rsync_tempfile_timeout` default derived from object-replicator config when possible. `audit_all_objects()` builds one audit-location generator per policy and processes them round-robin. `object_audit()` opens a diskfile, validates metadata, streams non-zero objects to verify content, invokes watchers, handles diskfile exceptions, and removes old rsync temp files. `failsafe_object_audit()` wraps each object audit so unexpected failures increment error counters instead of killing the whole pass.

`ObjectAuditor` is the daemon class used by `run_daemon()`. It parses config such as `devices`, `concurrency`, `zero_byte_files_per_second`, `interval`, `recon_cache_path`, and watcher names. `audit_loop()` supports parent-only zero-byte scans, single-process audits, and forked per-device parallel audits. `run_forever()` repeats passes with sleeps; `run_once()` runs a bounded pass with optional device filtering.

`WatcherWrapper` isolates watcher lifecycle calls: `start(audit_type)`, `see_object(object_metadata, data_file_path)`, and `end()`. It marks a watcher unusable after initialization/start/end failures but intentionally does not disable it after a single object-level `see_object` failure. A watcher can raise `QuarantineRequest` to request quarantine of a specific object.

`main()` defines CLI options for zero-byte-only scanning and device filtering, then starts `ObjectAuditor`.

## Control Flow
The daemon begins by loading watcher entry points from `swift.object_audit_watcher` and creating an `AuditorWorker`. For each policy in `POLICIES`, the worker asks the appropriate diskfile manager for an `object_audit_location_generator()`. Those iterators are interleaved with `round_robin_iter()` so one policy cannot monopolize an entire pass.

For each `AuditLocation`, `failsafe_object_audit()` calls `object_audit()`, then the worker records timing and applies file-rate throttling. Periodic logging happens every `log_time` seconds and writes a nested recon entry keyed by auditor type and device set.

Inside `object_audit()`, the diskfile is opened with `modernize=True`, so old metadata can be upgraded by the diskfile layer. The auditor reads metadata, calls `validate_metadata()`, and quarantines if required fields are missing. Non-zero objects are streamed through `df.reader(_quarantine_hook=raise_dfq)`, which lets reader-side checksum or length mismatches propagate as `DiskFileQuarantined`. Zero-byte-only mode skips non-zero body reads and uses its own configured files-per-second rate. Watchers observe successful metadata and data-file paths after the diskfile open/read phase; `QuarantineRequest` from a watcher is converted to a diskfile quarantine.

Deletion and expiration are not fatal. `DiskFileExpired`, `DiskFileDeleted`, and `DiskFileNotExist` are swallowed. Reclaimable tombstones encountered during full audits invalidate the containing suffix hash so replication or cleanup can converge later. Any unexpected files matching the rsync-tempfile pattern are removed if older than `rsync_tempfile_timeout`.

Process orchestration is handled in `ObjectAuditor.audit_loop()`. With `concurrency == 1`, one child scans all devices. With higher concurrency, the device list is shuffled and each child gets a device subset. If zero-byte scanning is enabled, a separate zero-byte scanner child is kept running during forever mode and optionally skipped after it completes in once mode.

## State, Persistence, And Dependencies
Persistent state is indirect. Audit progress is stored by `diskfile.object_audit_location_generator()` in `auditor_status_<type>.json` files under each policy data directory, allowing future passes to resume or avoid repeatedly starting from the same partition. Recon metrics are dumped into the object recon cache file under `RECON_OBJECT_FILE`. Quarantine is delegated to diskfile managers and physically moves corrupt hash or suffix directories under a device's `quarantined` tree. Stale rsync temp files are unlinked from object directories.

Runtime counters include pass-local `passes`, `quarantines`, `errors`, `bytes_processed`, and total counters used for final pass logs. Object-size bucket counts are maintained only for the current pass and emitted as logs when configured.

Dependencies include `swift.obj.diskfile` for audit-location generation and open/read/quarantine behavior, `swift.obj.replicator` only for timeout defaults, `swift.common.storage_policy.POLICIES`, eventlet-aware `Timeout`, rate limiting via `EventletRateLimiter`, recon cache helpers, plugin loading via `load_pkg_resource`, and daemon/config helpers from `swift.common.utils`.

## Integration Points
The object server and replication layers depend on the auditor to detect corrupt local object files and quarantine them so replication/reconstruction can replace data. The diskfile layer supplies policy-specific managers, audit locations, tombstone handling, and suffix invalidation. Recon tooling consumes the emitted object-auditor stats. Watcher plugins add extensibility for site-specific checks without changing the core auditor.

`auditor.py` is also tightly coupled to diskfile exception semantics: `DiskFileQuarantined` increments quarantine counts; `DiskFileDeleted` can trigger hash invalidation; `DiskFileExpired` is ignored because expiration is handled elsewhere; and `DiskFileNotExist` is a benign race or cleanup result.

## Risks
Watcher plugins run in-process and the wrapper notes that it does not isolate hangs or file descriptor leaks. A bad watcher can therefore degrade an audit worker. Process forking assumes POSIX semantics and manually resets `SIGTERM` plus `NOTIFY_SOCKET`; it is not portable outside Swift's expected deployment model.

The progress and recon status paths are best-effort. Corrupt or unreadable status JSON falls back to scanning all partitions, while write failures only warn. Audit throughput depends on correct rate-limit configuration; overly aggressive byte or file rates can create disk pressure, while overly low zero-byte rates can delay detection. The rsync tempfile cleanup heuristic relies on naming and timeout alignment with replicator behavior.

Because `object_audit()` increments `passes` even when it sees deleted, expired, or missing diskfiles, pass counts are "locations audited" rather than "healthy live objects." Tests and operator metrics need to interpret that correctly.

## Test Signals
High-value tests should exercise `AuditorWorker.object_audit()` with diskfiles that are valid, missing, deleted, expired, metadata-invalid, length-mismatched, and reader-checksum-mismatched. Watcher tests should cover successful callbacks, initialization/start/end failure, object-level callback failure, and `QuarantineRequest`. Daemon tests should cover single-process and multi-process audit selection, zero-byte scanner behavior, device filtering, recon cache writes, stale rsync tempfile removal, and status-file clearing after a pass.

Local repository test files were not present under this vendored source tree, so concrete validation signals are inferred from Swift's object-auditor contract and the function boundaries in this file.
