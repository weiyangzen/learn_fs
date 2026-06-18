# sources/storage-engines/foundationdb/fdbserver/workloads/ValidateStorage.cpp

## Purpose
`ValidateStorage` is a broad audit-storage correctness workload. It tests audit request submission, audit state querying, cancellation, progress persistence, direct storage-server audit requests, audit ID uniqueness, concurrent audits, and behavior under DD security and normal modes.

## Important APIs, Types, and Functions
Key types and APIs include `AuditStorageState`, `AuditType`, `AuditPhase`, `auditStorage()`, `cancelAuditStorage()`, `getAuditState()`, `getAuditStates()`, `getAuditStateByRange()`, `auditKeyRange()`, audit progress prefix helpers, `krmSetRange()`, `krmGetRanges()`, `decodeKeyServersValue()`, `serverListKeyFor()`, `decodeServerListValue()`, `AuditStorageRequest`, `StorageServerInterface::auditStorage`, `setDDMode()`, and `disableConnectionFailures()`.

## Control Flow
Only client 0 runs. `_start()` writes six test keys, disables audit-storage connection failures in simulation, checks string-to-phase parsing, sends direct storage-server validation requests for shards covering a range, then runs a sequence of audit tests. `auditStorageForType()` chooses a random audit range, triggers an audit, waits for completion or allowed clearing, and checks internal persisted state. Other tests verify ID generation, get-state behavior when no audit is ongoing, concurrent audits of different and same types, cancellation behavior, progress range persistence invariants, audits while DD is in security mode, and audits after DD returns to normal mode.

## State and Persistence Behavior
Persistent user data includes `TestKeyA` through `TestKeyF`. System state includes audit metadata, range/server progress records, audit phases, and DD mode. The workload checks that completed audits have no lingering progress rows and that retained completed/failed/running audit records stay within `PERSIST_FINISH_AUDIT_COUNT + 5`. It deliberately writes audit progress rows for synthetic progress tests.

## Dependencies and Integration Points
It integrates with audit client utilities, management API, Native API transactions, system key ranges, storage server interfaces, DD mode control, quiet database behavior, simulator connection-failure controls, and server/client knobs.

## Risks and Edge Cases
`disableFailureInjectionWorkloads()` excludes many workloads because DD mode and audit/storage behavior are sensitive to concurrent movement or corruption tests. `validationFailed()` sets `pass`, but `check()` currently returns true rather than `pass`, so many detected trace errors are not propagated through the workload return value. Empty audit ranges are accepted as failed audit submissions with invalid IDs. DD mode is changed to security and back to normal only on the normal path.

## Test Signals
Trace coverage is extensive: `ValidateStorageTestBegin`, `TestAuditStorageTriggered`, wait/error/end events, state persistence checks, cancellation errors, progress begin/end, DD mode audit completions, and many `SevError` traces for invariant violations. Hard assertions enforce many system-key and state invariants; the final `check()` is not the primary signal.
