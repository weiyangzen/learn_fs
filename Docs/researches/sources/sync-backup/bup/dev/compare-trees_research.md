# sources/sync-backup/bup/dev/compare-trees

## Purpose
Compares two filesystem trees as closely as bup can restore them, using rsync dry-run output as the difference oracle.

## Important APIs, Types, and Functions
Options include `-c`, `-x`, `--times`, `--no-times`, `--features`, and `--`. Builds rsync options `-rlpgoD -niH --delete` plus optional checksum, times, ACLs, and xattrs.

## Control Flow
Parses options, inspects `rsync --version` for ACL/xattr support, optionally prints feature support, runs rsync dry-run into a temp file, retries without `-X` if xattrs fail, and fails if any differences are reported.

## State and Persistence Behavior
Creates a temporary output file under `/tmp`; does not modify source/dest because rsync runs with `-n`.

## Dependencies and Integration Points
Used by restore/integration tests to compare bup output to source trees. Depends on rsync feature reporting and platform `OSTYPE`.

## Risks and Test Signals
Risks include rsync output semantics, unsupported ACL/xattr comparison, and timestamp policy differences. Signals are zero diff lines, feature output, and nonzero exit on differences.
