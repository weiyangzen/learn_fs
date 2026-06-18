# sources/storage-engines/tikv/tests/failpoints/cases/test_coprocessor.rs

Purpose: tests coprocessor error handling, deadline handling, paging scan ranges, follower read-index lock checking, bucket version propagation, and default-CF-not-found reporting.

Important APIs and functions: early tests inject `deadline_check_fail`, `coprocessor_parse_request`, `future_pool_spawn_full`, `rockskv_async_snapshot`, `kv_cursor_seek`, and `region_snapshot_seek`. Paging tests build `DagSelect` requests and parse `SelectResponse`. Later tests use grpc `TikvClient`, follower replica read context, in-memory locks, `Bucket`, and failpoints around stale-read safety and default CF loading.

Control flow: most tests initialize product-table data, build a coprocessor request, inject a failure or small batch size, call `handle_request`, and assert region/other errors or page ranges.

State and persistence: MVCC table data is written into test engines or raft engines; memory locks in concurrency manager must be observed by follower read-index checking. Bucket metadata is refreshed and then validated through response versions.

Dependencies and integration: integrates test coprocessor/table helpers, storage test engines, grpc clients, PD TSO, raftstore clusters, and TiDB datatype encoding.

Risks and test signals: paging range assertions are key-boundary sensitive. Signals cover user-visible coprocessor errors and resumable scan correctness.
