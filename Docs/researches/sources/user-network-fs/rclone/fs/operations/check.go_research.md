# sources/user-network-fs/rclone/fs/operations/check.go

## Purpose
`check.go` implements rclone's check and checksum-verification operations. It compares two filesystem trees by size/hash or by downloaded bytes, reports matches, differences, missing files, and errors into separate streams, and also supports validating a filesystem against a hash sum file.

## Important APIs, types, and functions
- `checkFn` is the injectable object comparison function used by `CheckFn`.
- `CheckOpt` carries source/destination filesystems, one-way mode, the comparison function, and output writers for combined and category-specific reports.
- `checkMarch` is the `march.March` callback implementation. It holds context, concurrency tokens, a wait group, output mutex, atomic counters, and copied options.
- `DstOnly`, `SrcOnly`, and `Match` classify tree-walk results into missing-on-source, missing-on-destination, type conflicts, or matched object pairs.
- `CheckFn` drives `march.March` and waits for concurrent object checks before summarizing.
- `Check` supplies hash/size comparison via `CheckHashes`.
- `CheckEqualReaders`, `CheckIdenticalDownload`, and `CheckDownload` implement byte-for-byte download verification.
- `ApplyTransforms` and `ToNormal` normalize checksum file paths for Unicode and case-insensitive matching.
- `CheckSum`, `HashSums`, `ParseSumFile`, `checkSum`, and `matchSum` validate filesystem objects against checksum files.

## Control flow
`CheckFn` builds a `checkMarch`, configures `march.March` with source, destination, traversal flags, and the callback, then runs the march. Directory-only callbacks recurse as needed; object matches spawn goroutines limited by `ci.Checkers`. Each comparison first checks size through `sizeDiffers`, honors `--size-only`, then delegates to the configured `checkFn`. Results are converted into sigils: `+` for source-only, `-` for destination-only, `=` for match, `*` for differ, and `!` for error.

`Check` sets `CheckOpt.Check` to a common-hash comparison. `CheckDownload` instead opens both objects, wraps them in accounting transfers, and compares buffered reads in 64 KiB blocks. `CheckSum` parses a sum file, lists destination objects, matches normalized object names against the parsed map, then performs either backend hash reads or downloaded hash streaming. Remaining unconsumed sums become missing-on-destination errors unless filtered out.

## State and persistence behavior
The file does not persist state itself. It mutates accounting counters, emits logs, writes to caller-provided writers, marks consumed checksum entries by overwriting map values with an empty string, and uses atomics for concurrent summary counters. Remote state is read-only except for implicit backend access caused by object opens and hash calls.

## Dependencies and integration points
The implementation integrates with `fs/accounting`, `fs/filter`, `fs/fserrors`, `fs/hash`, `fs/march`, `Open` from this package, `CheckHashes` and `sizeDiffers` from `operations.go`, synchronized output helpers, and `readers.ReadFill`. It is used by check-like commands and checksum commands, while tests exercise it through `operations.Check`, `CheckDownload`, and `CheckSum`.

## Risks and edge cases
Concurrency makes writer synchronization and counter accuracy important. `CheckEqualReaders` must prefer read errors over equality when an error appears after partial reads. Checksum parsing accepts only standard `hash  filename` or `hash *filename` shapes and suppresses warnings after three malformed or duplicate lines. Unicode normalization and case folding need to match `march.March` behavior so checksum validation aligns with normal check behavior. `CheckSum` uses a shared map across goroutines, so access is protected only around lookup/consume.

## Test signals
`check_test.go` covers normal check output categories, one-way mode, nonexistent filesystem errors, download checks, size-only behavior, reader equality and read-error propagation, checksum parsing, checksum validation in backend-hash and download modes, mixed-case checksums, and Unicode/case transform behavior.
