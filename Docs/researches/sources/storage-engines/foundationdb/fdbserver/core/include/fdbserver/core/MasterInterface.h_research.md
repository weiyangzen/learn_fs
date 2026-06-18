# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/MasterInterface.h

## Purpose
This header defines the RPC contract between commit proxies, cluster controller, and the master role for commit-version assignment, live committed-version reporting, recovery-data updates, and master lifetime validation.

## Important APIs, Types, And Functions
`MasterInterface` exposes `waitFailure`, `getCommitVersion`, `getLiveCommittedVersion`, `reportLiveCommittedVersion`, and `updateRecoveryData`. Request/reply types include `ChangeCoordinatorsRequest`, `ResolverMoveRef`, `GetCommitVersionRequest/Reply`, `UpdateRecoveryDataRequest`, `ReportRawCommittedVersionRequest`, and `LifetimeToken`. `CommitProxyVersionReplies` stores cached replies by request number with `NotifiedVersion` progress.

## Control Flow
`initEndpoints` registers adjacent endpoints with task priorities; serialization stores `waitFailure` and reconstructs adjusted endpoints on deserialization. Commit proxies request new commit versions, report processed request numbers, receive resolver movement changes, and report raw committed versions back to the master.

## State And Persistence Behavior
The interface is transient, but its messages carry persistent recovery and commit-version state: recovery transaction version, last epoch end, resolver/proxy lists, metadata version, min known committed version, written tags, and master lifetime token.

## Dependencies And Integration Points
It depends on commit proxy/resolver/TLog interfaces, database configuration, version vectors, storage server interfaces, Swift interop, and Flow notified values. It integrates with master recovery, commit proxy batching, live committed-version centralization, and coordinator changes.

## Risks And Edge Cases
Endpoint ordering is hard-coded through adjusted endpoints; adding streams requires careful compatibility. `LifetimeToken` logic protects against stale masters, so comparison bugs can cause split-brain-like behavior. Commit-version reply caching must erase only fully obsolete request numbers.

## Test Signals
Tests should cover endpoint round trips, monotonic commit-version replies, resolver-change propagation, stale lifetime rejection, live committed-version reporting with optional predecessor waiting, and recovery-data updates during master replacement.
