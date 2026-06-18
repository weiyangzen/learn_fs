# sources/sync-backup/bup/dev/sparse-size

## Purpose
Computes sparse/hole byte count for a file, using `SEEK_DATA/SEEK_HOLE` when available and `du` fallback otherwise.

## Important APIs, Types, and Functions
Bootstraps `dev/bup-python`, parses `-v`, uses `os.lseek`, `SEEK_HOLE`, `SEEK_DATA`, `ENXIO`, `getsize`, fallback `du -s`, `path-fs`, and `BLOCKSIZE=512`.

## Control Flow
With seek support, walks hole/data extents and sums holes, logging when verbose. Without seek support, waits on btrfs/zfs for allocation to settle, compares apparent size to `du`, and prints apparent minus allocated bytes.

## State and Persistence Behavior
Read-only file inspection; fallback sleeps but does not modify files.

## Dependencies and Integration Points
Used by sparse-file tests to verify restore/save sparseness.

## Risks and Test Signals
Risks are filesystem-specific allocation reporting, btrfs/zfs delay heuristics, and `du` block-size behavior. Signal is exact sparse byte count.
