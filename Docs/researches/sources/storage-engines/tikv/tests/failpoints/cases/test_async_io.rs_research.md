# sources/storage-engines/tikv/tests/failpoints/cases/test_async_io.rs

Purpose: verifies raftstore async IO semantics when leader or follower persistence is paused, snapshots are persisting, peers are removed, and unstable entry buffers shrink.

Important APIs and functions: test cases cover commit without leader persist, apply without leader persist, conf change while leader persist is skipped, delayed destroy after self-removal, snapshot-persist destroy/ready exclusion, and unstable entry shrink. Uses `#[test_case]` over v1/v2 clusters for several cases.

Control flow: tests pause or return from `raft_before_save_on_store_*`, `raft_before_persist_on_store_*`, or `raft_before_save_kv_on_store_*`, issue async puts/conf changes, and assert which stores can observe values before persistence resumes. Snapshot tests isolate a peer, wait for `MsgSnapshot`, then assert tombstone/ready processing is blocked until snapshot persistence completes.

State and persistence: explicitly distinguishes committed/applied data from persisted raft logs and persisted snapshot KV data. Uses engine reads and `unstable_entries_stat`.

Dependencies and integration: uses `test_raftstore`, packet filters, `MessageTypeNotifier`, PD client, and `tikv_util::HandyRwLock`.

Risks and test signals: strong timing dependence around snapshot delivery. Signals protect against data loss, premature destroy, and unbounded unstable entry buffers.
