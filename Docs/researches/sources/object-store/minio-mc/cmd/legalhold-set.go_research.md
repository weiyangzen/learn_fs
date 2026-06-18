# Research: sources/object-store/minio-mc/cmd/legalhold-set.go

Purpose: implements `mc legalhold set` and shared logic for applying legal hold status.

Important APIs/types/functions: `lhSetFlags`, `legalHoldSetCmd`, `setLegalHold`, `parseLegalHoldArgs`, and `mainLegalHoldSet`.

Control flow: `parseLegalHoldArgs` validates one non-empty target, disallows `--version-id` with recursive/version/rewind flags, and parses rewind. `mainLegalHoldSet` checks bucket locking and calls `setLegalHold` with enabled status. `setLegalHold` either calls `PutObjectLegalHold` directly or lists objects/versions and applies status to each listed object, printing per-object messages in console mode.

State and persistence: mutates object legal hold status server-side.

Dependencies/integration points: MinIO object-lock API, list behavior, alias expansion, `parseRewindFlag` from `ls-main.go`, and shared messages from legalhold main.

Risks: recursive set can touch many objects and versions. JSON recursive success output is suppressed by `if !globalJSON`, so scripts may not receive per-object success entries.

Test signals: no direct tests; should cover parser conflicts, empty target, direct set, recursive set, no objects found, and JSON behavior.
