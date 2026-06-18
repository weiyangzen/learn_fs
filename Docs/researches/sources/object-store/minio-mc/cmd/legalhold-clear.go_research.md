# Research: sources/object-store/minio-mc/cmd/legalhold-clear.go

Purpose: implements `mc legalhold clear`, disabling legal hold for one object, a version, or recursively listed objects/versions.

Important APIs/types/functions: `lhClearFlags`, `legalHoldClearCmd`, and `mainLegalHoldClear`.

Control flow: sets console colors, parses shared legalhold args, defaults `--versions` without `--rewind` to current time, verifies bucket locking is enabled, and calls `setLegalHold` with `minio.LegalHoldDisabled`.

State and persistence: mutates object legal hold status server-side.

Dependencies/integration points: shared parser and setter from legalhold set file, bucket-lock check from legalhold main, MinIO object lock APIs.

Risks: recursive clears are destructive for retention workflows. The command depends on correct bucket-lock detection before mutation.

Test signals: no direct tests; should cover version flag conflicts, bucket-lock disabled, and recursive clear behavior.
