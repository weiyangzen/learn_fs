# sources/object-store/daos/src/container/srv_target.c

## Purpose
Implements target-side container lifecycle, open-handle management, VOS and EC aggregation scheduling, snapshot notifications, OID allocation, target query/destroy/open/close collectives, property updates, and EC/stable epoch reporting. It is the main bridge between service-level container RPCs and per-xstream VOS container state.

## Important APIs and functions
- Aggregation: `cont_aggregate_interval()`, `cont_child_aggregate()`, `cont_vos_aggregate_cb()`, `cont_agg_ult()`, `cont_ec_agg_ult()`, `cont_start_agg()`, `cont_stop_agg()`, and `agg_rate_ctl()`.
- Target container cache: `ds_cont_child_cache_create()`, `cont_child_lookup()`, `cont_child_start()`, `cont_child_stop()`, `ds_cont_child_lookup()`, `ds_cont_child_open_create()`, `ds_cont_child_start_all()`, `ds_cont_child_stop_all()`.
- Handles: `ds_cont_hdl_hash_create()`, `ds_cont_hdl_lookup()`, `ds_cont_hdl_get/put()`, `ds_cont_local_open()`, `ds_cont_local_close()`, `ds_cont_tgt_open()`, `ds_cont_tgt_close()`.
- RPC handlers/aggregators: destroy, query, snapshot notify, epoch aggregate, and OID allocation handlers.
- Snapshot/OIT: `ds_cont_tgt_snapshots_update()`, `ds_cont_tgt_snapshots_refresh()`, `cont_snap_notify_one()`.
- Epoch tracking: `cont_tgt_track_eph_init/fini()`, `ds_cont_eph_report()`, `ds_cont_tgt_refresh_track_eph()` declaration partner, and `ds_cont_ec_timestamp_update()`.

## Control flow
Opening a target container goes through a pool thread collective. Each xstream either finds an existing `ds_cont_child` or creates a VOS container under the pool recovery read lock, starts aggregation ULTs unless the pool is restricted, registers DTX state, and inserts a `ds_cont_hdl` into TLS hash. First real open initializes DTX CoS, starts asynchronous DTX resync, and initializes checksum/dedup/compression/encryption properties from container IV. Closing removes the handle before yielding, decrements `sc_open`, and closes DTX state when the last handle closes. Destroy marks `sc_destroying`, force-closes handles, stops DTX reindex/scrub/rebuild/aggregation paths, evicts the LRU entry, destroys the VOS container, and wakes GC.

Aggregation loops periodically check pool map/stopping/rebuild/reclaim state, lazy/busy/space-pressure conditions, checksum/dedup/compression/encryption restrictions, snapshot IV readiness, and EC boundaries. `cont_child_aggregate()` computes an epoch range from HLC minus aggregation gap, last HAE, snapshot boundaries, EC aggregation boundaries, and snapshot deletion resets; it then invokes either VOS aggregation or EC object aggregation across ranges.

Snapshot notifications gather OIT OIDs when requested and cap aggregation during snapshot creation. Snapshot IV updates replace `sc_snapshots`, reset aggregation lower bound on deletion, and set `sc_aggregation_max`. Query collectives open VOS containers and reduce minimum HAE across xstreams. OID allocation reserves ranges through OID IV and returns the base OID. EC/stable epoch tracking stores pointers from each target into a per-pool system-xstream list and periodically publishes minimum nonfailed target epochs through container IV.

## State and persistence behavior
Persistent target state is mainly VOS containers and their object/DTX metadata. Volatile state includes TLS container cache entries, open handle hashes, scheduler requests, snapshot arrays, aggregation boundaries, checksum contexts, property mirrors, and epoch tracking arrays. Destroy deletes VOS persistence and invalidates container IV. OID allocation changes authoritative allocation state through IV backing logic, not local fields.

## Dependencies and integration points
Depends on VOS, DTX, DAOS scheduler, pool child/pool service, pool map/rebuild state, IV, checksum/dedup helpers, EC object aggregation, security capabilities, CaRT RPCs, and container RPC definitions. It is invoked by service leader code, pool startup/rebuild/destroy paths, object layer aggregation, checker failure injection, and snapshot/OIT code.

## Risks
This file is concurrency-sensitive: LRU refs, open-handle refs, `sc_destroying/sc_stopping`, DTX resync, scrub/rebuild waits, and aggregation ULT shutdown all interact. `ds_cont_tgt_query_handler()` asserts collective success and maps nonzero `rc` to `tqo_rc = 1`, which can hide details in release builds. `cont_child_aggregate()` copies snapshot arrays without a visible lock in this file, relying on update discipline. EC aggregation is disabled during rebuild and rate-limited by scheduler state, so stale boundaries can block VOS aggregation. Some target epoch aggregation RPC code is a placeholder (`cont_epoch_aggregate_one()` returns 0).

## Test signals
Existing engine/container integration should be supplemented with tests for repeated open with conflicting flags, first-open DTX/csummer failure cleanup, close after target down/downout, destroy races with rebuild/recovery, snapshot IV update/delete behavior, aggregation upper-bound calculation across snapshots/EC boundaries, OID IV failures, query reduction, property status PM-version ordering, and epoch reporting with failed targets.
