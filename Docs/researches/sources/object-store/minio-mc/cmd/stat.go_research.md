# sources/object-store/minio-mc/cmd/stat.go

## Purpose
Contains the core metadata retrieval and formatting logic for `mc stat`, including object stat messages and bucket-level metadata/usage display.

## Important APIs, types, and functions
- `statMessage` is the object metadata output model with fields for size, ETag, metadata, version, delete marker, restore state, checksum, expiration, and replication status.
- `statMessage.String` and `JSON` render text/JSON output.
- `parseStat` converts `ClientContent` to `statMessage`.
- `getStandardizedURL` normalizes paths for comparison.
- `statURL` orchestrates HEAD/stat, bucket info, listing, and version handling.
- `BucketInfo` models bucket properties: versioning, encryption, locking, replication, policy, location, tags, ILM, and notifications.
- `bucketInfoMessage` renders bucket info plus usage.
- `prettyPrintBucketMetadata` formats bucket configuration properties.

## Control flow
`statURL` creates a client, expands the target alias, computes prefix path handling, and chooses among several paths:
- `headOnly` or explicit `versionID`: call `url2Stat` directly and print object metadata.
- Non-recursive bucket/prefix without trailing slash: try `GetBucketInfo`, optionally fetch usage from admin `DataUsageInfo`, and print bucket info.
- Otherwise list with `ListOptions`, optionally including versions/delete markers and time reference, then for each listed content call `url2Stat`, trim prefix path, and print parsed stat messages.

It handles selected filesystem/list errors as non-fatal, skips Glacier storage class objects, verifies non-recursive prefix matching, filters by version ID when necessary, and returns object-missing when no entries are found.

## State and persistence
Read-only. It reads object metadata, bucket configuration, and admin data usage. No state is written.

## Dependencies and integration points
Uses client list/stat/admin abstractions, MinIO admin `DataUsageInfo`, lifecycle/notification/replication models, encryption key DB, `humanize`, `colorjson`, console themes, and global time/format constants.

## Risks and edge cases
- Bucket info path is attempted before list path for non-recursive targets without trailing slash.
- `statMessage.String` separates recognized encryption headers from general metadata; unrecognized encryption headers display "Unknown".
- Listing path calls `url2Stat` per object, which can be expensive for large recursive stats.
- `found` increments before filters such as Glacier skip and version ID filtering, so "not found" behavior can differ from "no printable stat".
- Bucket usage is best-effort; admin client failures leave usage zero.

## Test signals
`stat_test.go` covers `parseStat` metadata copying, size, expiry pointer behavior, type detection, and ETag quote trimming. More tests should cover bucket formatting, version/delete marker output, encryption metadata recognition, and `statURL` branch behavior.
