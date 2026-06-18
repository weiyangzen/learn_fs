# sources/object-store/minio-mc/cmd/retention-info.go

## Purpose
Implements `mc retention info`, showing object retention for a single object/version, a recursive/listed set, or the default bucket object-lock configuration.

## Important APIs, types, and functions
- `retentionInfoFlags` mirrors the clear command with `--recursive`, `--version-id`, `--rewind`, `--versions`, and `--default`.
- `parseInfoRetentionArgs` validates one target and bucket-mode flag conflicts.
- `retentionInfoMessage` is the shared data model.
- `retentionInfoMessageList` renders compact list output for multi-object mode.
- `retentionInfoMessageRecord` renders detailed single-object output.
- `retentionInfoMsg` abstracts setters plus the `message` interface.
- `infoRetentionSingle` calls `GetObjectRetention` and prints either list or record style.
- `getRetention` handles single-object, bucket fallback, and listed recursive/version modes.

## Control flow
`mainRetentionInfo` configures colors, parses flags, verifies bucket lock support, dispatches to `showBucketLock` for `--default`, injects current UTC rewind for `--versions` without `--rewind`, then calls `getRetention`.

`getRetention` validates S3-only support and expands aliases. In direct mode it calls `infoRetentionSingle`; if the direct stat represents an empty object name, it falls back to `showBucketLock`, which makes bucket URLs behave as bucket default inspection. In list mode it uses `ListOptions`, skips delete markers, stops in non-recursive exact-object mode, prints list-style records, and returns an error exit status when no object/version is found.

## State and persistence
Read-only against remote retention state. No local persistence. The output status changes to failure for per-object errors but successful no-retention states are represented as mode empty.

## Dependencies and integration points
Depends on shared retention utilities, `newClient`, `newClientFromAlias`, MinIO `GetObjectRetention`, `showBucketLock`, `parseRewindFlag`, and global output/error helpers.

## Risks and edge cases
- `fatalIfBucketLockNotSupported` runs before both bucket and object info.
- `NoSuchObjectLockConfiguration` is treated as a successful "no retention" object response; other errors print failures except `ObjectNameEmpty`.
- List output marks governance entries expired when `now.After(until)` but compliance mode list output does not show an expiration label.
- The error string in list style has a duplicated "get get".

## Test signals
No direct tests in this subset. Coverage should include direct object info, no-lock behavior, bucket URL fallback, version/list traversal, and JSON failure status handling.
