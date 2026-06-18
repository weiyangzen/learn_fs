# sources/storage-engines/foundationdb/fdbcli/GetAuditStatusCommand.cpp

Purpose: Implements `get_audit_status`, a diagnostic command for fetching audit records, recent/phase-filtered audit states, and progress for multiple audit types.

Important APIs/types/functions: `getAuditStatusCommandActor`, `getAuditProgress`, `getAuditProgressByRange`, `getStorageServers`, `getAuditProgressByServer`, fdbclient audit APIs `getAuditState`, `getAuditStates`, `getAuditStateByRange`, and `getAuditStateByServer`, plus `AuditStorageState`, `AuditType`, and `AuditPhase`.

Control flow: The command maps type tokens (`ha`, `replica`, `locationmetadata`, `ssshard`, `validate_restore`, `metadata_encoding`) to `AuditType`, then branches on `id`, `progress`, `recent`, and `phase`. `id` fetches one audit state by UID. `recent` fetches newest states with optional count. `phase` filters by parsed phase and optional count. `progress` fetches the audit state, and if running, delegates to progress helpers. Range-based audit progress pages through audit state ranges, printing ongoing/error ranges and count of finished ranges. Storage-server-shard progress lists storage servers, skips TSSes, and classifies each server as complete/ongoing/error/partial.

State and persistence behavior: Read-only diagnostic against audit metadata and server list system keys. No local state.

Dependencies and integration points: Depends on audit metadata layout, audit utility functions, server list decoding, system-key reads, `CLIENT_KNOBS->TOO_MANY`, and fdbcli output formatting.

Risks: `getAuditStatusCommandActor` checks `tokens.size() < 2 || > 5` but then accesses `tokens[2]`; a two-token invocation with only a type can index past the vector. Progress loops call `auditStates.back()` and assume non-empty range results. Retry counters are shared across pages and can end progress early after repeated transient failures.

Test signals: Cover all action forms, invalid type/action/phase, missing action token parser safety, count parsing, range progress with ongoing/error/complete states, storage-server-shard progress including TSS skip, empty audit-state result handling, and retry exhaustion.
