# sources/storage-engines/foundationdb/fdbclient/AuditUtils.cpp

## Purpose

`AuditUtils.cpp` implements shared data-distribution audit utilities. It manages audit metadata lifecycle, progress persistence, cleanup, cancellation, resume initialization, move-keys lock validation, range comparison helpers, and readers that compare `serverKeys` and `keyServers` metadata for location consistency audits.

## Important APIs, Types, and Functions

- Metadata lifecycle: `persistNewAuditState`, `persistAuditState`, `getAuditState`, `cancelAuditMetadata`, `clearAuditMetadataForType`, and `initAuditMetadata`.
- Progress metadata: `persistAuditStateByRange`, `getAuditStateByRange`, `persistAuditStateByServer`, `getAuditStateByServer`, `checkAuditProgressCompleteByRange`, and `checkAuditProgressCompleteByServer`.
- Cleanup routing: `clearAuditProgressMetadata` chooses range-based or server-based progress keyspaces based on `AuditType`.
- Locking: `checkMoveKeysLockForAudit` validates and optionally takes/touches the move-keys lock using `MoveKeyLockInfo`.
- Query helpers: `getAuditStates`, `checkStorageServerRemoved`, and `stringToAuditPhase`.
- Range/location helpers: `coalesceRangeList`, `rangesSame`, `checkLocationMetadataConsistency`, `buildLocationMetadataMaps`, `buildOwnRangesFromServerKeysResult`, `buildOwnershipMapFromKeyServersResult`, `getThisServerKeysFromServerKeys`, and `getShardMapFromKeyServers`.

## Control Flow

Most functions run retry loops with system-immediate priority, system-key access or reads, and lock-aware transactions. New audit creation takes the move-keys lock, reads the latest audit ID for a type, assigns the next ID, and commits the encoded `AuditStorageState`. Final state persistence verifies the audit was not cancelled, optionally clears progress on complete, and writes the terminal state. Progress persistence first checks the DD-owned audit state, updates DD ID after failover, skips if already complete, rejects failed/cancelled audits, then writes a KRM range under range-based or server-based progress prefixes. Completion checks page through progress ranges until all subranges have non-invalid phases.

`initAuditMetadata` runs when the data distributor starts or recovers: it loads all audit states, updates running states to the current DD ID, clears old complete/failed audits beyond the retention count, keeps failed progress for investigation until selected for cleanup, and returns running audits to resume. Location metadata helpers build normalized maps from `keyServers` and `serverKeys`, coalesce ranges, and report mismatches by server ID and range.

## State and Persistence Behavior

The file persists audit state under `auditKeys`, progress under either range-based or server-based KRM keyspaces, and move-keys lock ownership/write markers under lock keys. Complete audits clear progress metadata; failed/error audits generally retain progress metadata for investigation until cleanup. Running audits are updated with the current DD ID during initialization so resumed work belongs to the active distributor.

## Dependencies and Integration Points

The utilities integrate with `Audit.h` data encoding, `SystemData.h` audit key builders, KRM helpers, `NativeAPI.actor`, `ReadYourWrites`, client knobs, move-keys locking, storage-server metadata, key-server/server-key encoders, and Flow tracing. They are used by data distribution audit actors and CLI audit status/cancel paths.

## Risks and Edge Cases

Audit correctness depends on consistent routing of each `AuditType` to the right progress keyspace; `clearAuditProgressMetadata` uses explicit branches and `UNREACHABLE` for unknown types. Some cleanup is intentionally non-atomic across read and clear. `persistNewAuditState` compares only `UID.first()` for sequencing and assumes no concurrent creator can pass the move-keys lock. Completion checks access `auditStates.back()` after reads; callers rely on KRM reads returning boundary rows. Retry loops often continue until success except for actor cancellation, move-key conflicts, or bounded progress-check retries. Location range comparison assumes sorted, exclusive ranges in simulation and may assert on invalid inputs.

## Test Signals

This file is not directly exercised by `fdbcli_tests.py` except through audit CLI commands elsewhere. Strong test signals would include simulated DD failover/resume, audit cancellation, progress persistence by range/server, complete versus failed cleanup behavior, move-keys lock conflict paths, `rangesSame` mismatch cases, and consistency comparison between synthetic `serverKeys` and `keyServers` KRM results.
