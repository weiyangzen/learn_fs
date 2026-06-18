# sources/object-store/minio-mc/cmd/retention-set.go

## Purpose
Implements `mc retention set`, applying governance/compliance retention to objects or setting default bucket retention.

## Important APIs, types, and functions
- `retentionSetFlags` defines object/list flags and `--bypass` plus `--default`.
- `parseSetRetentionArgs` validates `MODE VALIDITY TARGET`, mode validity, `Nd`/`Ny` retention duration, target, and bucket-mode conflicts.
- `setRetention` delegates object/list mutation to `applyRetention`.
- `setBucketLock` delegates default bucket retention to `applyBucketLock`.
- `mainRetentionSet` wires parsing, support checks, default rewind behavior, and execution.

## Control flow
The command accepts exactly three positional arguments. It uppercases and validates retention mode with MinIO's `RetentionMode.IsValid`, parses validity through `parseRetentionValidity`, and rejects `--default` combined with object/list/bypass flags. Bucket mode directly calls `setBucketLock`; object mode checks object-lock support, injects current UTC rewind for all-versions mode when needed, and applies retention through shared listing/single-object logic.

## State and persistence
Persists remote object retention or bucket default object-lock configuration. No local files are changed.

## Dependencies and integration points
Uses `retention-common.go`, MinIO `RetentionMode` and `ValidityUnit`, CLI/global context, `parseRewindFlag`, and console output helpers.

## Risks and edge cases
- `--bypass` is rejected for bucket defaults but allowed for object governance mutations.
- Validity parsing is byte-suffix based, so callers rely on prior argument count and non-empty input.
- `--versions` without `--rewind` applies to versions visible as of command start time.
- Compliance retention can create irreversible remote state subject to server policy.

## Test signals
No direct tests. Tests should cover mode validation, validity parsing, `--default` conflicts, and delegation parameters for object vs bucket mode.
