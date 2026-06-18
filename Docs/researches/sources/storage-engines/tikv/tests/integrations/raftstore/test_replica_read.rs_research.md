<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_replica_read.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_replica_read.rs

## Purpose
This file tests replica read and read-index correctness under unapplied logs, hibernation, stale peers, out-of-order read-index responses, lock checking retries, split isolation, snapshot peer replacement, malformed read-index messages, and pending peers.

## Important APIs, Types, and Functions
`CommitToFilter` records commit indexes per peer and clears commit fields in outgoing raft messages. Tests use `async_read_on_peer`, `async_read_index_on_peer`, `ReadIndexContext`, `block_on_timeout`, `RegionPacketFilter`, `DropSnapshotFilter`, `IsolationFilterFactory`, `configure_for_lease_read`, `configure_for_hibernate`, `Lock`, `LockType`, and concurrency-manager lock guards.

## Control Flow and Behavior
The not-applied test blocks followers from seeing commits, transfers leadership to a follower with an uncommitted first entry, verifies follower reads block instead of returning old values, releases append responses, and checks retry completion. Hibernation tests block read-index traffic, observe pre-vote wakeups, and verify hibernated leaders can be woken by extra messages after PD leader info loss.

Stale and out-of-order tests block appends or heartbeat responses to ensure reads time out or later resolve after peer removal. Lock retry tests insert an in-memory lock on one key and confirm delayed read-index responses report locked only for the affected key. Split isolation and snapshot replacement tests ensure local reader delegates are updated after split/snapshot and peer ID replacement. Malformed read-index sends an entry with `request: None` and verifies the read queue still serves a subsequent valid request. Pending-peer tests return `read_index_not_ready`.

## State and Persistence
The tests inspect applied values on each engine, read response errors, read-index lock fields, local reader delegate freshness, hibernation wakeup messages, and snapshot-created peer state. They rely on raft log commit/applied indexes and transaction lock memory.

## Dependencies and Integration Points
The file integrates raftstore local reads, raft read-index protocol, hibernate-region wakeup messages, PD membership updates, snapshots, concurrency manager locks, UUID-encoded read contexts, and v1/v2 node cluster variants.

## Risks
Risks include stale local reads, blocked reads never retrying, malformed read-index corrupting the queue, local reader caching an obsolete peer ID after snapshot replacement, hibernated leaders not waking, and pending peers serving reads before they are safe.

## Test Signals
Signals are timeout vs success boundaries, expected `v1`/`v2` values, `not_leader`, `read_index_not_ready`, locked read-index fields, captured wakeup extra messages, absence of mismatch-peer-id errors, and successful reads after filters clear.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_replica_read.rs -->
