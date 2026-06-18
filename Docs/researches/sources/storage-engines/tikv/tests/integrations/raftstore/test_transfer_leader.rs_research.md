# sources/storage-engines/tikv/tests/integrations/raftstore/test_transfer_leader.rs

## Purpose
This file validates leader transfer through direct admin requests and PD scheduling, including multi-target selection, transfer prevention during snapshot state, max-ts synchronization after transfer, and in-memory pessimistic lock handling during successful or failed transfer.

## Important APIs, Types, and Functions
It uses `new_transfer_leader_cmd`, `pd_client.transfer_leader`, `must_transfer_leader`, `MessageType::MsgTimeoutNow`, `SnapshotFilter`, `tikv::storage::Snapshot`, `LocksStatus`, `PessimisticLock`, `LastChange`, `Key`, and the lock CF `CF_LOCK`.

## Control Flow
Basic transfer tests warm address resolution, ensure the target follower has latest entries, issue transfer, then verify the old leader rejects direct writes with `not_leader`. PD transfer tests loop over target peers and confirm commands succeed on the elected leader. The multi-target test isolates one lagging peer, asks PD to transfer to a candidate list, and expects the up-to-date peer to win. Snapshot-state transfer test blocks snapshot packets and `MsgTimeoutNow`, then confirms normal writes do not hang. Timestamp and pessimistic-lock tests transfer leadership and verify concurrency-manager max ts or lock materialization/status.

## State and Persistence Behavior
The tests verify committed KV data on engines, lock CF persistence after in-memory locks are proposed during transfer, and in-memory lock table status transitions from `TransferringLeader` back to `Normal` after failed transfer.

## Dependencies and Integration Points
The file integrates PD operator scheduling, raft leader transfer messages, raftstore/v2 cluster variants, storage snapshot transaction extensions, lock CF persistence, TSO failure injection, and network filters.

## Risks
Leader transfer regressions can produce stale leaders accepting commands, transfer to lagging snapshot peers, lost in-memory locks, or unsynchronized max timestamps after leadership changes. Failed transfer must also restore lock-table availability.

## Test Signals
Signals include leader identity assertions, successful direct reads on new leaders, `not_leader` from old leaders, writes completing while a follower is in snapshot state, `new_max_ts > old max_ts`, lock bytes present in `CF_LOCK`, and `LocksStatus` returning to `Normal`.
