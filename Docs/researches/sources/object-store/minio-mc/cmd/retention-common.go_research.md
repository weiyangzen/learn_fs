# sources/object-store/minio-mc/cmd/retention-common.go

## Purpose
Provides shared object-lock and retention behavior for `retention set`, `clear`, and `info`: message types, validity parsing, per-object retention application, recursive/version listing, bucket default lock application, and bucket default lock display.

## Important APIs, types, and functions
- `retentionCmdMessage` and `retentionBucketMessage` implement text/JSON output for object and bucket retention operations.
- `lockOpType` and constants `lockOpInfo`, `lockOpClear`, `lockOpSet` identify operation mode.
- `getRetainUntilDate` computes RFC3339 retain-until timestamps from day/year validity.
- `setRetentionSingle` uses `newClientFromAlias` and `PutObjectRetention` for a single object/version.
- `parseRetentionValidity` parses `Nd`/`Ny` retention duration strings.
- `fatalIfBucketLockNotSupported` checks bucket lock support.
- `applyRetention` handles single-object or listed-object retention mutation.
- `applyBucketLock` sets, clears, or fetches bucket object-lock config.
- `showBucketLock` reads bucket object-lock config for display.

## Control flow
`applyRetention` validates that the target resolves to an `S3Client`, computes `retainUntil` only for set operations, expands aliases, and chooses a single-object path when `versionID` is present or neither recursive nor versions is requested. Otherwise it lists with `ListOptions`, optionally including older versions and delete markers for rewind/version mode. It skips delete markers, stops early in non-recursive exact-object mode, calls `setRetentionSingle`, tracks whether any eligible object/version was found, and returns an exit status if none were processed.

`applyBucketLock` creates a client, uses a cancelable global context, calls `SetObjectLockConfig` for set/clear or `GetObjectLockConfig` for info-like behavior, then prints a `retentionBucketMessage`.

## State and persistence
All state changes are remote object-lock mutations. `setRetentionSingle` persists object retention. `applyBucketLock` persists bucket default object-lock configuration. Shared messages include operation status and errors for scriptable output.

## Dependencies and integration points
Uses MinIO client abstractions (`newClient`, `newClientFromAlias`, `List`, `PutObjectRetention`, `SetObjectLockConfig`, `GetObjectLockConfig`), alias utilities, `ClientContent` list metadata, `probe.Error`, and console/global print helpers.

## Risks and edge cases
- `parseRetentionValidity` assumes a non-empty string and indexes the last byte; callers must ensure syntax.
- Delete markers are skipped because object retention cannot be applied to them.
- `applyRetention` fatal-exits for non-S3 clients.
- Non-recursive listed mode compares standardized URLs and breaks once it moves past the target object.
- The bucket message says "Object locking is not enabled" when mode is invalid, even if the raw enabled status has other nuance.

## Test signals
No direct tests in this subset. Important tests would cover validity parsing, zero validity rejection, list filtering, delete marker skipping, S3-only enforcement, and bucket lock set/clear/info branching.
