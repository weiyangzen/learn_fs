# sources/storage-engines/tikv/components/raftstore-v2/src/operation/command/admin/transfer_leader.rs

## Purpose
Implements raftstore-v2 transfer-leader handling, including a pre-transfer readiness protocol that warms entry cache and optionally drains pessimistic locks before raft leadership transfer.

## Important APIs, Types, And Functions
`transfer_leader_cmd` extracts `TransferLeaderRequest`. `Peer::propose_transfer_leader` selects a transferee and sends pre-transfer messages. `pre_transfer_leader`, `on_transfer_leader_msg`, `maybe_reject_transfer_leader_msg`, `set_pending_transfer_leader_msg`, `maybe_ack_transfer_leader_msg`, `maybe_transfer_leader_cache_warmup`, `ack_transfer_leader_msg`, and `ready_to_transfer_leader` implement the message lifecycle. `Apply::apply_transfer_leader` and `Peer::on_transfer_leader` handle the optional proposed transfer-leader command.

## Control Flow
The current leader picks the candidate with the highest matched index from requested peers, randomizing ties, and sends `MsgTransferLeader` with the leader's entry-cache first index and term. A follower rejects if it is snapshotting, the sender is not the current leader, or disk-full conditions would reduce availability; otherwise it stores the message and waits until cache warmup and coprocessor pre-ack hooks are ready or a deadline expires. It then ACKs with its applied index. When the leader receives the ACK, it checks voter membership, pending snapshots, pending conf changes, and log lag. If locks must be proposed first, it proposes a flagged `TransferLeader` admin command; after the target applies that command it ACKs with `CommandReply`. Otherwise the leader calls raft `transfer_leader`.

## State And Persistence Behavior
Most state is transient in transfer-leader state: pending message, deadline, and cache warmup range. The optional `TransferLeader` admin command is replicated but only returns `AdminCmdResult::TransferLeader` when the expected new leader is the local peer; it does not mutate region metadata. Cache warmup state is reset when stale and updated as async cache population progresses.

## Dependencies And Integration Points
Integrates with raft progress/status, entry cache warmup, coprocessor `pre_ack_transfer_leader`, transaction lock proposal before transfer, admin dispatch flags, disk usage, config timing, and raft message queues.

## Risks And Edge Cases
Transfer is refused for learners/non-voters, pending snapshots, pending conf changes, log gaps beyond `leader_transfer_max_log_lag`, wrong term, and unsafe disk-full combinations. Deadlines prevent indefinite cache warmup blocking. Rolling upgrade compatibility is handled by accepting index zero. Term mismatch during apply causes stale transfer commands to be ignored.

## Test Signals
No tests are local here. Signals include transfer-leader proposal metrics, logs for rejection reasons, cache warmup state transitions, ACK messages with applied indexes, and raft transferee refresh after `transfer_leader`.
