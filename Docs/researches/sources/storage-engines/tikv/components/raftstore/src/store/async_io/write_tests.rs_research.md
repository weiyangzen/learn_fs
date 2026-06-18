# sources/storage-engines/tikv/components/raftstore/src/store/async_io/write_tests.rs

Purpose: Provides unit and integration-style tests for `store::async_io::write` and some write-router/resource-control interactions. The file builds test engines, notifiers, transports, workers, and writer pools to validate durable state and asynchronous notifications.

Important APIs and types: Helpers include `must_have_entries_and_state`, `new_raft_state`, `TestNotifier`, `TestTransport`, `TestWorker`, `TestWriters`, `init_write_batch`, KV/raft put-delete helpers, and notification/message assertions. It aliases test KV write batches and raft log batches for readability.

Control flow: Tests construct `WriteTask`s with combinations of KV extra writes, raft log batches, appended entries, raft states, apply/region states, callbacks/messages, then either add them directly to a worker batch or send them through `StoreWriters` senders. Assertions inspect snapshots, raft-engine entries/states, apply/region states, message receivers, notification receivers, and success timestamp atomics.

State and persistence behavior validated: `test_worker` verifies KV extra writes, raft log append/overwrite/delete, latest ready notification per region, outbound messages, and raft/KV success timestamps. `test_worker_split_raft_wb` validates splitting raft log batches while preserving apply states and final raft state. `test_basic_flow` and `test_basic_flow_with_states` validate asynchronous pool behavior for v1 and v2 state paths. Resource-group testing verifies entry headers drive I/O resource accounting through the write router.

Dependencies and integration points: The tests depend on `engine_test` temporary KV/raft engines, `resource_control`, raft command protobufs, raftstore `WriteRouter`, `Config`, local metrics, and peer-storage test entry helpers. They exercise both direct worker methods and spawned writer threads.

Risks: Several async assertions use timeouts, which can be sensitive to overloaded CI. Tests using random write-router selection loop until the desired state appears in `write_router.rs`, while this file mostly routes deterministically by sender id. The tests are strong on persistence invariants but do not simulate disk write failures beyond failpoints present in production code.

Test signals: This file is itself the test signal. It covers adaptive wait clamping, high/low QPS paths, futile-wait reduction, zero adaptive threshold validation/runtime guard, no oscillation at high QPS, worker persistence, split batches, basic spawned writers, v2 state writes, and resource-group scheduling.
