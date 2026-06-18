# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/TLogInterface.h

## Purpose
This header defines the transaction-log role RPC interface and message types for peeking, popping, committing, locking, metrics, snapshots, recovery completion, and recovery tracking.

## Important APIs, Types, And Functions
`TLogInterface` exposes streams for `peekMessages`, `peekStreamMessages`, `popMessages`, `commit`, `lock`, queue metrics, confirm running, wait failure, recovery finished, pop disable/enable, snapshot, and recovery tracking. Message types include `TLogLockResult`, `UnknownCommittedVersions`, `VerUpdateRef`, `TLogPeekRequest/Reply`, `TLogPeekStreamRequest/Reply`, `TLogPopRequest`, `TagMessagesRef`, `TLogCommitRequest/Reply`, `TLogQueuingMetricsRequest/Reply`, `TLogDisablePopRequest`, `TLogEnablePopRequest`, `TLogSnapRequest`, and `TrackTLogRecoveryRequest/Reply`.

## Control Flow
Commit proxies send `TLogCommitRequest` batches with versions and serialized messages. Storage servers/log routers peek from a begin version by tag, optionally through streaming replies. Consumers pop durable versions. Recovery locks logs, discovers unknown committed versions, confirms running logs, and waits for old generations to recover.

## State And Persistence Behavior
Requests carry durable log versions, known committed versions, message blobs, tag locations, snapshot IDs, and queue metrics. Endpoint serialization stores one base endpoint and reconstructs adjusted endpoints by fixed index.

## Dependencies And Integration Points
It depends on FDB types, commit transactions, timed requests, storage bytes, span context, and RPC streams. It is central to master recovery, commit proxies, storage servers, log routers, backup, snapshots, and ratekeeper queue metrics.

## Risks And Edge Cases
Endpoint index ordering is compatibility-critical. Version chain gaps, incorrect popped versions, unknown committed versions, sequence IDs, and streaming acknowledgement handling can break recovery or durability.

## Test Signals
Signals include commit/peek/pop ordering, recovery lock correctness, log router and storage catch-up, queue metrics accuracy, disable/enable pop around snapshots, streaming peek backpressure, and old-generation recovery tracking.
