# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/local.rs

## Purpose
Implements the v2 local snapshot reader. It serves snapshot reads directly from a cached tablet when region validation, applied term, lease, and stale-read safe-ts checks allow; otherwise it redirects through the peer FSM to perform read-index and then retries.

## Important APIs, Types, And Functions
`MsgRouter` abstracts sending `PeerMsg` to a peer. `SharedReadTablet` owns a shareable tablet handle whose cached clone is deliberately short-lived. `LocalReader::snapshot` is the public async entry point. Internals include `pre_propose_raft_command`, `try_get_snapshot`, `try_to_renew_lease`, and `maybe_renew_lease_in_advance`. `CachedReadDelegate` pairs a `ReadDelegate` with a `SharedReadTablet`. `StoreMetaDelegate` implements `ReadExecutorProvider` for `LocalReaderCore`. `SnapRequestInspector` selects `ReadLocal`, `ReadIndex`, or `StaleRead`.

## Control Flow
`snapshot` first attempts local execution synchronously. Request validation fetches a cached delegate from store metadata, fills the tablet cache, verifies the request is exactly one `Snap`, and inspects policy. For local reads it snapshots the tablet before reading time, fences ordering, checks the remote leader lease, fills v2 snapshot metadata, and optionally sends an advance-renewal query. For stale reads it decodes the read timestamp from header flag data, checks safe-ts before and after snapshot acquisition, and returns the snapshot only if safe. For read-index policy or expired lease, it sends a read-quorum `PeerMsg::RaftQuery`, waits for a `QueryResult::Read`, clears `read_quorum`, and retries local snapshot acquisition.

## State And Persistence Behavior
The reader does not write persistent state. It reads from store metadata and tablet snapshots, attaches transaction extension state, term, txn extra op, bucket metadata, and v2 marker to the returned `RegionSnapshot`. `SharedReadTablet` drops the underlying optional tablet when the source wrapper is dropped, allowing stale tablets to be released even if clones exist. Safe-ts and leader lease are read from `ReadDelegate`/`RegionReadProgress`.

## Dependencies And Integration Points
Depends on `LocalReaderCore`, `ReadDelegate`, `RegionSnapshot`, store metadata readers, router query channels, `ReadProgress`, `TxnExt`, bucket metadata, `WriteBatchFlags::STALE_READ`, local read metrics, and tracker metrics. It is paired with lease handling in `query/lease.rs` and read progress updates in `query/mod.rs`.

## Risks And Edge Cases
The snapshot path must avoid reading from a stale tablet after epoch changes; failure to fill the tablet cache causes retry. Local reads require applied term equal to current term and a valid remote leader lease. Stale reads must check safe-ts both before and after snapshot acquisition. The retry limit of ten protects against infinite stale delegate loops but turns persistent churn into an internal error. Router full and disconnected errors are converted to server-busy or region-not-found responses.

## Test Signals
`test_read` covers unregistered regions, applied-term mismatch requiring read-index retry, lease expiration and renewal, tablet cache misses, read-quorum routing, and stale-read safe-ts failures/success. `test_read_delegate` checks that delegate tablet handles match expected tablet paths and are released after reader removal. Failpoints `perform_read_index` and `perform_read_local` force policy selection.
