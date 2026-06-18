# sources/object-store/openstack-swift/swift/common/db_auditor.py

## Purpose
`db_auditor.py` defines `DatabaseAuditor`, the base daemon for account and container database auditors. It scans database files, opens brokers, skips deleted DBs, runs subclass-specific checks, rate-limits audit throughput, logs pass/failure counts, and writes recon cache metrics.

## Important APIs, types, and functions
- `DatabaseAuditor` inherits `Daemon`.
- `rcache` builds the recon cache file path from `recon_cache_path` and `server_type_to_recon_file(server_type)`.
- Abstract properties `server_type` and `broker_class` are implemented by account/container auditor subclasses.
- `__init__()` loads devices, mount-check mode, interval, max DBs per second, recon path, datadir, logger, rate limiter, and DB preallocation setting.
- `_one_audit_pass(reported)` iterates DB locations from `audit_location_generator()`, audits each DB, periodically logs and dumps recon counters, and rate-limits between DBs.
- `run_forever()` adds a randomized initial sleep, loops audit passes, handles exceptions/timeouts, dumps pass completion timing, and sleeps for the remaining interval.
- `run_once()` performs one pass and dumps completion timing.
- `audit(path)` creates a broker, checks deletion state, gets info, delegates to `_audit(info, broker)`, and updates pass/failure metrics.
- `_audit(info, broker)` is an abstract subclass hook.

## Control flow
An audit pass walks `<devices>/<device>/<server_type>s/**/*.db` through `audit_location_generator()` with optional mount checking. Each path is passed to `audit()`, which constructs the subclass broker, calls `is_deleted()`, then reads `get_info()` and runs subclass-specific validation. A returned exception object from `_audit()` is raised so all audit failures share the same accounting path. Every logging interval, pass/failure counters since the last report are logged and dumped to recon, then reset.

Forever mode waits a random fraction of the configured interval before the first pass to avoid synchronized cluster-wide scans. Each loop logs start/completion, catches broad exceptions and eventlet `Timeout`, increments error metrics, writes elapsed pass time to recon, and sleeps only if the pass finished faster than the configured interval.

## State and persistence behavior
The auditor is mostly read-only for database content, but opening brokers may commit pending files depending on broker behavior, and `DB_PREALLOCATION` is set globally from config. It writes recon cache JSON through `dump_recon_cache` and emits logger counters/timings. It keeps in-memory pass/failure counters that reset after each recon report.

## Dependencies and integration points
It depends on `Daemon`, eventlet `Timeout`, `audit_location_generator`, `EventletRateLimiter`, config parsing helpers, recon cache naming, and subclass broker classes. Account and container auditor daemons derive from this base to add DB-specific consistency checks.

## Risks and edge cases
Because broker `is_deleted()` and `get_info()` can touch pending commits, audits are not purely passive on DB side effects. Broad exception handling keeps the daemon alive but can mask repeated systemic failures unless recon/log metrics are monitored. Randomized initial sleep is useful operationally but must be controlled in tests. Misconfigured `max_dbs_per_second` can make passes slower than the interval, causing continuous auditing without sleep. Mount-check behavior determines whether unmounted drives are skipped or scanned as directories.

## Test signals
Tests should cover config defaults and overrides, recon path naming, rate limiter calls, logging interval counter resets, deleted DB skip behavior, subclass `_audit()` success and returned-exception failure, broker construction errors, timeout handling, forever-mode sleep calculations, run-once recon output, and `DB_PREALLOCATION` global mutation.
