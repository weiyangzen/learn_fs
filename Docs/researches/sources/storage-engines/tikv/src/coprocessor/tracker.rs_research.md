# sources/storage-engines/tikv/src/coprocessor/tracker.rs

## Purpose
Tracks lifecycle timing, storage scan statistics, perf context counters, slow logs, read-flow metrics, and execution details for legacy coprocessor requests.

## Important APIs, Types, and Functions
`TrackerState` models a strict request lifecycle from `Initialized` through `Tracked`. `Tracker<E>` stores request context, request tag, timing accumulators, storage statistics, slow-log threshold, scan process time, optional bucket metadata, and engine type marker. Public transition methods include `on_scheduled`, `on_snapshot_finished`, `on_begin_all_items`, `on_begin_item`, `on_finish_item`, `on_finish_all_items`, and collectors for storage stats and scan process time. `get_item_exec_details` and `get_exec_details` build legacy and v2 `kvrpcpb::ExecDetails`. `FutureTrack` integration maps future polling to item begin/finish. `Drop` fast-forwards partially completed trackers so metrics are still emitted.

## Control Flow
Normal flow is initialize, schedule, retrieve snapshot, build handler, process one or more items, then finish all items. Each transition asserts the previous state. Item processing starts perf observation and finishes by reporting perf metrics to TLS tracker tokens. `track` emits slow logs when processing plus suspend time exceeds threshold, records histograms/counters, collects read flow for select/index tags, and reports MVCC read activity to `MVCC_READ_TRACKER` using perf context skipped-key counters.

## State and Persistence Behavior
State is transient per request. Effects persist only through metrics registries, TLS coprocessor metrics, slow logs, and MVCC read tracker observations. `Drop` mutates state to close unfinished lifecycles and may log deadline-exceeded warnings if the request deadline has passed.

## Dependencies and Integration Points
Depends on engine perf context traits, `kvproto` exec detail protobufs, `pd_client::BucketMeta`, tracker TLS APIs, coprocessor metrics, `ReqContext`, `ReqTag`, storage `Statistics`, and MVCC read tracking. It is a bridge between coprocessor request execution and observability.

## Risks and Edge Cases
Most public transition methods use `unreachable!` on invalid order, so callers must preserve lifecycle ordering. `Drop` can emit metrics for failed or abandoned paths, which is intentional but can obscure partial execution if interpreted as successful work. Perf context TLS is keyed by `ReqTag`; missing new tags would panic or omit metrics unless added to `with_perf_context`. Time conversions cast nanoseconds to `u64`, which is practically safe but relies on request durations remaining bounded.

## Test Signals
`test_track` checks read-flow collection only for select-like tags and validates bucket-level stats are collected for query traffic but not analyze traffic. There is limited direct coverage of state-machine invalid paths, slow-log fields, exec detail construction, deadline logging, and MVCC read tracker integration.
