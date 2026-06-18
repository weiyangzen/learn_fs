# sources/object-store/garage/src/rpc/rpc_helper.rs

Purpose: high-level RPC orchestration: single calls, broadcasts, quorum reads, write-set quorum writes, request ordering, block read node ordering, and quorum result tracking.

Important APIs and types: `RequestStrategy` configures quorum, send-all behavior, priority, timeout, and drop-on-complete payload. `RpcHelper` wraps peer manager, layout, metrics, local node ID, and timeout. Public methods include `call`, `call_many`, `broadcast`, `try_call_many`, `try_write_many_sets`, and `block_read_nodes_of`. `QuorumSetResultTracker` tracks successes/failures across overlapping quorum sets.

Control flow: `call` performs a streaming endpoint call under OpenTelemetry context and a selectable timeout, translating NetApp and Garage errors into metrics. `try_call_many` orders nodes by locality/latency, sends only enough requests to reach quorum unless `send_all_at_once`, and stops once quorum succeeds or becomes impossible. `try_write_many_sets` sends to every unique node immediately, waits for quorum in every write set, and moves unfinished requests to a background task after success so broadcast writes can still complete on lagging replicas.

State and persistence: no persistence. Runtime state is per-call futures and metric counters.

Dependencies and integration: core dependency for `System`, layout manager, table GC/sync, and higher storage layers. Uses Garage NetApp endpoint abstractions, layout versions, peering ping state, OpenTelemetry, and `RecordDuration`.

Risks and test signals: dropping read-style futures cancels remote handlers, which is intentional but unsuitable for writes. `try_write_many_sets` relies on tracker correctness for overlapping layout versions. Node ordering assumes current layout has zone data. No direct tests in file; exercised by table/system integration.
