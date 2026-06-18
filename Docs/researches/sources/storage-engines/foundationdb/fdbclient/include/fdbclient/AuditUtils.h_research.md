# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/AuditUtils.h

Purpose: declares helpers for persisting audit metadata, checking audit progress, and comparing key ownership metadata.

Important APIs and types: includes metadata operations such as `cancelAuditMetadata`, `persistNewAuditState`, `persistAuditState`, `getAuditState(s)`, range/server progress persistence, cleanup, and initialization. Ownership helpers include `AuditGetServerKeysRes`, `AuditGetKeyServersRes`, `coalesceRangeList`, `rangesSame`, `LocationMetadataError`, `LocationMetadataMaps`, parsers for ServerKeys/KeyServers results, and transaction readers.

Control flow: callers persist top-level audit state, persist progress by range or server, then use completeness checks to determine whether a claimed range/server audit is finished. Location metadata checking builds normalized maps from the two system keyspaces and compares coverage.

State and persistence: functions operate on FoundationDB system metadata through `Database` and `Transaction`, often guarded by `MoveKeyLockInfo` and DD ownership. Result structs carry read versions, byte counts, ranges, and ownership maps.

Dependencies and integration: includes `Audit.h`, `NativeAPI.actor.h`, `FDBTypes.h`, and `fdbrpc.h`; integrates data distributor, storage servers, and system keyspace encodings.

Risks: range coalescing/equivalence must handle adjacent splits without false mismatches. Audit ownership must handle DD failover via `ddId`. Progress checks are budgeted for server-based audits, so starvation or partial reads need care.

Test signals: audit simulation tests should validate metadata resume/cleanup, range/server completeness, and consistency errors for mismatched KeyServers/ServerKeys maps.
