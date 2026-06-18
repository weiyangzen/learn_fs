# sources/object-store/minio-mc/cmd/retention-clear.go

## Purpose
Implements `mc retention clear`, clearing object retention settings for one object/version or a listed set of objects, plus `--default` bucket object-lock configuration clearing.

## Important APIs, types, and functions
- `retentionClearFlags` defines `--recursive`, `--version-id`, `--rewind`, `--versions`, and `--default`.
- `retentionClearCmd` registers the CLI command.
- `parseClearRetentionArgs` validates one target and rejects object/list flags when bucket default mode is requested.
- `clearRetention` delegates object-level work to `applyRetention` with `lockOpClear`, no mode, zero validity, and governance bypass forced true.
- `clearBucketLock` delegates bucket-level work to `applyBucketLock`.
- `mainRetentionClear` wires validation, object-lock support checking, default rewind behavior, and execution.

## Control flow
The command parses the target and flags, configures retention colors, checks object-lock support with `fatalIfBucketLockNotSupported`, then either clears the bucket default retention config or applies clear retention to the object/list target. If `--versions` is set without `--rewind`, it uses the current UTC time as the list time reference.

## State and persistence
Mutates remote S3/MinIO object-lock state. Object mode clears per-object retention using `PutObjectRetention` through shared code; bucket mode changes the bucket object-lock configuration. No local state is persisted.

## Dependencies and integration points
Depends on `retention-common.go` for shared retention messages and apply logic, `parseRewindFlag`, MinIO object-lock APIs, global context, and CLI/global output helpers.

## Risks and edge cases
- `--default` is mutually exclusive with object-scoped flags, preventing ambiguous bucket/object operations.
- Governance bypass is always enabled for clear, which is powerful and depends on server-side permissions.
- `fatalIfBucketLockNotSupported` runs before bucket mode too; unsupported remotes fail early.
- `--versions` without `--rewind` snapshots at current UTC, which can surprise users expecting all historical versions independent of a time reference.

## Test signals
No direct tests in this subset. Useful tests would cover flag conflict validation, default rewind injection, and that clear delegates with `bypassGovernance=true`.
