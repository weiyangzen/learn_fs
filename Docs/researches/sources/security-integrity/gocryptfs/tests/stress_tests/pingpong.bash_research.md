# sources/security-integrity/gocryptfs/tests/stress_tests/pingpong.bash

## Purpose
Runs an infinite move-and-verify stress test that shuttles the Linux 3.0 tree between two gocryptfs mounts using plain `mv`.

## Important APIs, Types, And Functions
- `move_and_md5` chooses plain `mv` when the basename is not `pingpong-rsync.bash`.
- The loop verifies the moved tree against `linux-3.0.md5sums` after each hop.

## Control Flow
The script prepares two independent gocryptfs mounts, extracts the source tree once, then alternates moving it between mounts and validating checksums.

## State And Persistence
State is two temp cipherdirs and mountpoints under `/tmp`, removed by the EXIT trap.

## Dependencies And Integration Points
Depends on gocryptfs, tar, md5sum, renice, and the shared unmount helper.

## Risks And Edge Cases
It is unbounded and intentionally churns large directory trees. Plain `mv` exercises rename-heavy behavior rather than rsync copy/unlink behavior.

## Test Signals
A pass is continued iteration with no checksum mismatch and no remaining source tree after each move.
