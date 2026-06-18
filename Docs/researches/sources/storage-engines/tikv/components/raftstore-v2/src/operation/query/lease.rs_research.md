# sources/storage-engines/tikv/components/raftstore-v2/src/operation/query/lease.rs

## Purpose
Implements leader lease and leader-side read-index behavior for raftstore-v2 queries. It decides when reads can be answered under lease, when quorum read-index is required, and how lease state is propagated to local read delegates.

## Important APIs, Types, And Functions
`Peer::on_step_read_index` handles incoming read-index messages when a leader has a valid lease. `pre_read_index` blocks unsafe read-index during split or merge. `read_index_leader` proposes or amends leader read-index requests. `respond_read_index` returns read responses after read-index completion. `maybe_renew_leader_lease`, `expire_lease_on_became_follower`, `maybe_update_read_progress`, `inspect_lease`, `try_renew_leader_lease`, and `need_renew_lease_at` maintain lease state. `PeerFsmDelegate::on_check_leader_lease_tick` periodically renews the lease.

## Control Flow
For a leader read, the peer first checks whether the latest pending read can be amended under the current lease. If so, it batches the command with that read and records the local committed index. Otherwise it calls raft `propose_read_index`, stores a `ReadIndexRequest`, and marks ready. If the lease is suspect, it proposes a no-op write to refresh the lease. Completed read-index requests bind tracker timing, recheck region epoch, merge locally recorded committed index with the batch read index, and return `QueryResult::Read`.

## State And Persistence Behavior
Lease state is in memory but published into `StoreMeta.readers` as `ReadProgress` so `LocalReader` can make local-read decisions. Leadership changes expire or renew lease state and update read delegates. Read-index requests are in-memory pending-read queue entries; they do not persist by themselves, although no-op writes used for lease renewal enter the raft log.

## Dependencies And Integration Points
Depends on raft-rs read-index APIs, `ReadIndexRequest`, `ReadProgress`, `ReadDelegate`, store metadata, proposal control, leader lease utilities, `SimpleWriteEncoder` for no-op writes, query channels, tracker metrics, and `PeerTick::CheckLeaderLease`.

## Risks And Edge Cases
The code deliberately uses peer-storage commit index rather than raft-rs committed index to avoid exposing reads beyond persisted/applied state. Split and merge states reject read-index to avoid stale range ownership. Epoch is checked again at response time because the region may split or merge while read-index is pending. A leader transfer marks lease suspect on `MsgTimeoutNow`, requiring explicit renewal. The `before_propose_readindex` failpoint can inject read-index failure.

## Test Signals
No local unit tests are in this file. Signals include read-index pending metrics, leader lease ticks, failpoint injection, local-reader tests that observe lease renewal effects, and integration tests for leader transfer, split/merge read safety, and read quorum behavior.
