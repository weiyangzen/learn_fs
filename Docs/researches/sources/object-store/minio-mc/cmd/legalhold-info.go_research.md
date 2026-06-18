# Research: sources/object-store/minio-mc/cmd/legalhold-info.go

Purpose: implements `mc legalhold info`, showing legal hold status for objects and versions.

Important APIs/types/functions: `lhInfoFlags`, `legalHoldInfoCmd`, `legalHoldInfoMessage`, `showLegalHoldInfo`, and `mainLegalHoldInfo`.

Control flow: parses args and bucket-lock status, then either fetches legal hold directly for a single object or lists matching objects/versions and fetches hold status for each. Console output prints status, optional version ID, and key. JSON output for recursive mode suppresses per-object prints in current code path.

State and persistence: read-only object-lock query.

Dependencies/integration points: MinIO client `GetObjectLegalHold`, list APIs, alias expansion, `parseRewindFlag`, and common legalhold colors.

Risks: recursive error handling can continue after per-object failures, returning only listing errors as exit status. JSON behavior in recursive path appears incomplete because successful recursive items are only printed when not JSON.

Test signals: no direct tests; cover single-object JSON, recursive console, not-found object/version, and bucket-lock disabled.
