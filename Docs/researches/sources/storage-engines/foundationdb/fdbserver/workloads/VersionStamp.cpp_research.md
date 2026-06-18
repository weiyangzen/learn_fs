# sources/storage-engines/foundationdb/fdbserver/workloads/VersionStamp.cpp

## Purpose
`VersionStampWorkload` stress-tests versionstamped values and versionstamped keys across API versions, commit-unknown-result handling, optional extra database validation, and metadata-version-key behavior.

## Important APIs, Types, and Functions
The workload uses `MutationRef::SetVersionstampedValue`, `SetVersionstampedKey`, `ReadYourWritesTransaction::getVersionstamp()`, `metadataVersionKey`, `metadataVersionRequiredValue`, `ClusterConnectionMemoryRecord`, simulated extra databases, `ApiVersion`, and watch support. Helpers include `keyForIndex()`, `versionStampKeyForIndex()`, `endOfRange()`, `versionFromValue()`, `versionFromKey()`, `_start()`, and `_check()`.

## Control Flow
Client 0 chooses API version 500, 510, 520, or latest, sets `allowMetadataVersionKey`, and runs `_start()` at a Poisson transaction rate. Each loop chooses a value key, versionstamped key, and clear range; constructs old or new versionstamp formats depending on API version; optionally disables RYW; performs versionstamped value and key atomic ops; clears the previous versionstamped-key range; optionally watches metadata-related keys; commits and records committed version/versionstamp in in-memory maps. Commit-unknown-result recovery reads back the written value to decide whether to record the commit. `_check()` reads value and key prefixes at a stable read version, parses embedded versions, and compares them with recorded commit maps.

## State and Persistence Behavior
Persistent data lives under configurable prefixes `K_` and `V_`, with optional writes to `metadataVersionKey`. The workload records expected histories in `key_commit` and `versionStampKey_commit`; these are local process state and are used as the check oracle. Optional extra database validation reads from a simulated extra database instead of the primary.

## Dependencies and Integration Points
It integrates with Native API versioned behavior, RYW transactions, metadata version key rules, simulation extra database policy, versionstamp wire formats before and after API 520, and transaction watches.

## Risks and Edge Cases
Correctness depends on local commit history surviving for the whole workload. Commit-unknown-result recovery can classify a commit as unknown if the readback key is absent or already known. Metadata version key handling is special because other actors may write it unless `soleOwnerOfMetadataVersionKey` is set. `cx->apiVersion` is mutated on the database object, which affects later transaction behavior for this workload.

## Test Signals
Assertions in `_check()` validate size, parsed version bounds, recorded histories, and versionstamp byte equality. Traces include `VersionStampApiVersion`, `VST_CommitFailed`, and `VST_CheckEnd`. `check()` returns `_check()` on client 0.
