# sources/storage-engines/foundationdb/fdbserver/workloads/RestoreValidation.cpp

## Purpose
`RestoreValidationWorkload` schedules and monitors a `ValidateRestore` audit after another workload finishes a prefixed backup/restore validation flow. It waits for a completion marker, starts audit storage validation over `normalKeys`, and fails if the audit does not reach the expected phase.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `RestoreValidation`. Important options are `validateAfter`, `expectedPhase`, `expectSuccess`, `checkInterval`, and `maxWaitTime`. `_start` uses `auditStorage`, `getAuditStates`, `AuditStorageState`, `AuditType::ValidateRestore`, `AuditPhase`, `IClusterConnectionRecord`, system-key reads, `LOCK_AWARE`, and several audit-specific errors.

## Control Flow
Only client 0 runs. It delays by `validateAfter`, then polls the system key `\xff\x02/restoreValidationComplete` until present, retrying known transient errors. It schedules a validate-restore audit with a 60-second scheduling timeout, then polls audit states every `checkInterval`, filtering by the returned audit ID. It reports progress every ten seconds, enforces `maxWaitTime`, and retries the whole audit up to five times on `audit_storage_failed`.

## State And Persistence Behavior
The workload does not write user data. It reads a system completion marker and creates audit storage metadata through the management API. Audit state is durable cluster metadata managed by the audit subsystem, not by this workload directly.

## Dependencies And Integration Points
It is designed to coordinate with `BackupAndRestoreValidation`, which creates the restored prefix and writes the marker. It depends on `fdbclient/Audit.h`, `AuditUtils`, `ManagementAPI`, and the cluster connection record. It is sensitive to buggify-induced recovery delays and includes retry/backoff paths for cluster instability.

## Risks And Edge Cases
There is no maximum wait for the completion marker beyond the surrounding simulation timeout, by design. Audit states can temporarily disappear or time out during recovery; the workload logs warnings but continues until overall timeout. The `expectedPhase` option is stored but the success path primarily checks `AuditPhase::Complete` when `expectSuccess` is true.

## Test Signals
Success emits `RestoreValidationSuccess` with the audit ID. Failures include `RestoreValidationTimeout`, `RestoreValidationUnexpectedPhase`, `RestoreValidationUnexpectedError`, `RestoreValidationUnexpectedSuccess`, and `RestoreValidationError`. `check` itself returns true; actor errors are the real signal.
