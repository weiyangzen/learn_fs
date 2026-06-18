# sources/storage-engines/tikv/tests/failpoints/cases/test_metrics_overflow.rs

## Purpose
This file tests a narrow memory-metrics overflow path for raft messages to ensure overflow checking does not incorrectly panic in peer receive accounting.

## Important APIs, Types, and Functions
- `test_memory_metrics_overflow` builds a three-node server cluster.
- It sets `store_batch_system.pool_size = 1` to make store disk usage/memory information available on the target thread.
- Failpoints `memtrace_raft_messages_overflow_check_send` and `memtrace_raft_messages_overflow_check_peer_recv` control the overflow path.

## Control Flow
The test starts the cluster, pauses the send-side overflow check briefly, sets the peer-receive overflow check to panic, then performs a put and get. If the receive-side overflow path were incorrectly reached, the test would panic.

## State and Persistence Behavior
The persisted state is minimal: a single key is written and read to force raft message traffic. The focus is volatile memory metric accounting and overflow guard behavior.

## Dependencies and Integration Points
This test integrates raftstore message flow, memory tracing failpoints, and basic cluster put/get paths.

## Risks and Test Signals
The risk is an overflow accounting bug that triggers peer-receive panic or corrupts memory metrics under delayed send accounting. The signal is successful `must_put` and `must_get` with the panic failpoint enabled.
