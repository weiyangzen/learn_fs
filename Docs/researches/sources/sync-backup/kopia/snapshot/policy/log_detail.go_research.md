# sources/sync-backup/kopia/snapshot/policy/log_detail.go

Purpose: defines numeric log-detail levels used by snapshot logging policy.

Important APIs/types/functions: `LogDetail` integer type with constants `LogDetailNone` (0), `LogDetailNormal` (5), and `LogDetailMax` (10). `OrDefault` returns a default for nil pointers. `NewLogDetail` returns a pointer.

Control flow: straightforward nil-aware defaulting and pointer construction.

State and persistence behavior: values persist as JSON integers when used in policy structs; pointer fields allow omitting unset values.

Dependencies/integration: used by `logging_policy.go` and upload logging code.

Risks: numeric values are part of persisted policy semantics. Consumers must use pointer-aware defaulting to distinguish unset from zero/none.

Test signals: `log_detail_test.go` verifies JSON omitempty behavior and round-trip of pointer/non-pointer values.
