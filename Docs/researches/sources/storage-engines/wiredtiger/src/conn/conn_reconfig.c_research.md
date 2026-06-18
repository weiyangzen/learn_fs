# sources/storage-engines/wiredtiger/src/conn/conn_reconfig.c

## Purpose
This file implements connection reconfiguration support plus related connection-level configuration helpers for compatibility version, operation tracking, and statistics selection.

## Important APIs, Types, and Functions
Important exported functions are `__wti_conn_compat_config`, `__wti_conn_optrack_setup`, `__wti_conn_optrack_teardown`, `__wti_conn_statistics_config`, and `__wti_conn_reconfig`. Local helper `__conn_compat_parse` parses release strings. Important state includes `conn->cfg`, `compat_version`, `compat_req_min`, `compat_req_max`, `optrack`, `stat_flags`, and `reconfig_lock`.

## Control Flow and Behavior
Compatibility parsing accepts major.minor or major.minor.patch strings and rejects versions newer than the library. Compatibility configuration handles default current-version mode, upgrade/downgrade quiescence checks, required min/max checks, saved turtle compatibility validation, and turtle rewrite on reconfigure under the turtle or live-restore path.

Operation tracking setup stores the configured path at open, rejects read-only mode, creates a process-ID-qualified map file, initializes its spin lock and dummy-session buffer, and sets `WT_CONN_OPTRACK`. Teardown destroys the spin lock, closes the map file, frees buffers, and optionally frees the path on close.

Statistics configuration parses mutually exclusive `none`, `fast`, and `all`, then optional `cache_walk`, `tree_walk`, and `clear`, with a live-restore guard that prevents disabling stats.

`__wti_conn_reconfig` serializes with `reconfig_lock`, replaces `cfg[0]` with current connection config, detects a fast path for disaggregated-only updates, and otherwise runs all subsystem reconfigurers in an explicit order. It then merges config back into `conn->cfg`, excluding transient disaggregated checkpoint metadata and last-materialized LSN.

## State and Persistence
Reconfig updates volatile connection state and, for compatibility changes, rewrites turtle metadata. Operation tracking creates/removes files. Statistics flags are connection state. The saved connection config string is replaced atomically enough under `reconfig_lock`.

## Dependencies and Integration Points
This file integrates with transaction quiescence, metadata turtle rewriting, live restore, block cache, optrack, page history, stats, cache, eviction, shared cache, load control, capacity/checkpoint servers, debug/diagnostics, disaggregated storage, history store, log manager, statlog, tiered storage, sweep, timing stress, JSON, verbose, and rollback-to-stable.

## Risks
Risks include reconfiguration order dependencies, accidentally preserving transient disaggregated config, changing compatibility while operations/checkpoints are active, restarting statlog too aggressively, operation-tracking resource leaks on partial setup, and fast-path disaggregated updates skipping a dependent history-store reconfiguration when more than last-materialized LSN changes.

## Test Signals
Signals include compatibility upgrade/downgrade tests, quiescence enforcement, turtle rewrite behavior, reconfigure idempotence, disaggregated fast-path reconfig tests, statistics option validation, live-restore statistics guard, and operation tracking enable/disable resource cleanup.
