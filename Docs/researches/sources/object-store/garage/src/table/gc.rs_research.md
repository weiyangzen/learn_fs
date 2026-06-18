# sources/object-store/garage/src/table/gc.rs

Purpose: garbage collection for table tombstones. It waits a delay, ensures all replica nodes have observed a tombstone, then deletes the tombstone locally and remotely if still equal.

Important APIs and types: `TableGc<F, R>` owns `System`, `TableData`, and a `GcRpc` endpoint. `GcRpc` has `Update`, `DeleteIfEqualHash`, and `Ok`. `GcWorker` drives background work. `GcTodoEntry` encodes todo keys as tombstone timestamp plus table key and stores the tombstone value hash.

Control flow: `gc_loop_iter` scans `gc_todo` by timestamp, waits until the earliest deletion time, filters candidates whose current table value still hashes to the tombstone hash, removes stale todos, groups live tombstones by remote storage-node set, and runs `try_send_and_delete`. That method sends tombstone values to every other replica with quorum equal to all nodes, then asks them to delete if their value hash still matches, then deletes locally and removes todos. RPC handlers apply updates or compare-delete hashes.

State and persistence: persistent state is the `gc_todo_v2` DB tree and main table rows. GC does not delete unless all target nodes respond, so failures leave todos for retry.

Dependencies and integration: depends on table replication, RPC helper quorum calls, background worker API, table update/delete primitives, and wall-clock `now_msec`.

Risks and test signals: GC correctness is safety-critical because premature deletion can resurrect old CRDT values. It intentionally requires all remote nodes, trading liveness for safety. Layout changes during GC can alter storage sets. No direct tests here; behavior is integration-level.
