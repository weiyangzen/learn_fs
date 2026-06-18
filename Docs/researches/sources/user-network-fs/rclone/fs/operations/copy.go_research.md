# sources/user-network-fs/rclone/fs/operations/copy.go

## Purpose
`copy.go` implements single-object copy behavior, including server-side copies, streamed/manual copies, multi-threaded copies, partial upload names, transfer-limit checks, retry handling, verification, and the exported `Copy`/`CopyFile` entry points.

## Important APIs, types, and functions
- `copy` stores one copy operation's destination filesystem/features, destination object, remote names, source object, config, common hash, transfer accounting, partial-upload state, and retry limit.
- `removeFailedCopy` and `removeFailedPartialCopy` clean up failed objects.
- `TruncateString` safely truncates byte length while preserving valid UTF-8 where possible.
- `checkPartial` chooses the real remote or a stable hashed partial remote based on config and destination features.
- `checkLimits` enforces `--max-transfer` with hard, cautious, and graceful cutoff semantics.
- `serverSideCopy`, `manualCopy`, `multiThreadCopy`, `rcat`, and `updateOrPut` implement the copy strategies.
- `verify` validates post-transfer size and hash.
- `Copy` prepares accounting and operation state; `CopyFile` invokes shared move/copy file logic.

## Control flow
`Copy` creates an accounting transfer, honors `SkipDestructive`, transforms the destination path, selects a common hash, resolves partial naming, and calls `copy.copy`. The copy loop checks transfer limits, tries server-side copy when the backend supports it and configs are compatible, falls back to manual copy on `fs.ErrorCantCopy`, and retries retriable or `Retry-After` errors up to low-level retry limits.

Manual copy builds upload and download open options from hash, headers, and metadata config. It chooses multi-thread copy when `doMultiThreadCopy` allows it, otherwise opens the source and uses `rcat` for unknown-size streams or `Put`/`Update` for known-size objects. On success it verifies size and hash, then renames a partial object into place when partial uploads were used. On failure it removes partial files or corrupt copies.

## State and persistence behavior
The operation creates, updates, deletes, or renames remote objects. Partial uploads use stable suffixes derived from destination name and source fingerprint, and failed partials are removed both through deferred cleanup and an `atexit` handler. Accounting transfer state is reset on retries and finalized through `tr.Done`.

## Dependencies and integration points
This file depends on `fs.Features` methods such as `Copy`, `Move`, `Put`, and object `Update`; accounting transfers; `CommonHash`, `Open`, `Rcat`, `rcatSrc`, `moveOrCopyFile`, `SkipDestructive`, and `sizeDiffers` from the operations package; `fserrors`, `pacer`, `atexit`, and path/name transforms. It is a core dependency for sync, move, copy command paths, and multi-thread copy.

## Risks and edge cases
Partial names must not exceed backend filename limits and must avoid collisions for long names. `TruncateString` has to preserve valid UTF-8 without corrupting invalid byte strings unexpectedly. Server-side copies may count bytes differently, so accounting is rewound on fallback. Verification must avoid leaving corrupt destination files. Unknown-size streams cannot use ordinary `Put` semantics. Max-transfer cutoff behavior differs by mode and can be affected by server-side copies.

## Test signals
`copy_test.go` covers UTF-8 truncation, basic copy idempotency, maximum local filename length, backup-dir moves, compare-dest and copy-dest behavior, in-place versus partial copy, long partial-name collisions, and max-transfer cutoff modes.
