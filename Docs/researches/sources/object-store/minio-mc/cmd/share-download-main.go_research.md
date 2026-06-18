# sources/object-store/minio-mc/cmd/share-download-main.go

## Purpose
Implements `mc share download`, generating presigned download URLs for one or more S3 objects or recursively listed object sets, and saving generated shares locally.

## Important APIs, types, and functions
- `shareDownloadFlags` defines `--recursive`, `--version-id`, and `--expire`.
- `checkShareDownloadSyntax` validates target presence, expiry bounds, `--version-id`/`--recursive` conflict, and direct object existence.
- `doShareDownloadURL` expands aliases, stats target, chooses direct or listed object flow, calls `ShareDownload`, prints messages, and saves shares.
- `mainShareDownload` parses encryption keys, initializes share config, sets colors, parses expiry, and processes all targets.

## Control flow
Syntax validation parses expiry duration and enforces 1 second to 7 days. For non-recursive targets it stats objects up front using encryption keys. During execution, `doShareDownloadURL` loads the downloads DB, stats the target via the client, emits one object for file targets or lists a directory/prefix, skips directories, creates a new client per object URL, generates a presigned download URL with optional version ID, stores it in the DB, and prints a `shareMessage`. After all objects are processed, the DB is saved.

## State and persistence
Writes generated download shares to the local downloads DB returned by `getShareDownloadsFile`. It also prunes expired entries as a side effect of `Load`.

## Dependencies and integration points
Depends on share config and DB helpers, MinIO client `Stat`, `List`, and `ShareDownload`, encryption-key parsing for stat validation, alias expansion, `ClientContent`, and global output/fatal helpers.

## Risks and edge cases
- Recursive sharing still calls `Stat` before listing; targets that cannot be statted fail early.
- Version ID is only allowed for non-recursive direct targets.
- The function opens and saves the DB once per target, so multiple targets in one invocation are safe sequentially but separate processes can race.
- Non-S3 clients return `APINotImplemented` and are reported as unsupported.

## Test signals
No direct tests in this subset. Tests should cover expiry validation, recursive/version conflict, direct object existence validation, DB updates, and list/direct generation behavior.
