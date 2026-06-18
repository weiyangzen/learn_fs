# sources/test-tools/stress-ng/stress-dentry.c

## Purpose
This filesystem stressor thrashes directory entries by creating many files, probing existing and nonexistent names, performing miscellaneous directory operations, and unlinking files in selectable orders. It is designed to stress dentry cache, lookup failure paths, unlink ordering, and filesystem metadata operations.

## Important APIs, Types, And Functions
`stress_dentry_removal_t` maps order names to constants for forward, reverse, stride, and random removal. `stress_dentry_unlink_file()` removes one file and optionally verifies stored gray-code content first. `stress_dentry_unlink()` removes a full batch in the selected order. `stress_dentry_state()` reads Linux `/proc/sys/fs/dentry-state` for cache deltas. `stress_dentry_misc()` opens the temp directory and exercises `utime`, `fstat`, illegal reads/truncates/fallocate, mmap, futimens, select, locks, and fcntl. `stress_dentry()` is the main workload.

## Control Flow
The stressor reads `dentries` and `dentry-order`, creates a temporary directory, captures initial dentry count, and enters a loop. It creates files named from gray-coded values multiplied by two, optionally writes the gray code for verification, and increments bogo count. It then performs directory misc operations, syncs, probes existing files and generated nonexistent files, times bogus unlinks, increments an offset to avoid name reuse, unlinks the real files in forward/reverse/stride/random order, and repeats. On abort it computes dentry delta, emits timing metrics, force-unlinks remaining files, and removes the temp directory.

## State And Persistence
Persistent state is temporary files under the stress-ng temp directory until cleanup. Verify mode stores an 8-byte gray-code value in each file. Metrics track nanoseconds per file creation, existing access, bogus access, and bogus unlink. Linux dentry-state deltas are informational only.

## Dependencies And Integration Points
Dependencies include stress-ng temp-file helpers, prime helper for stride order, mmap helpers, optional file locking/select/utime/futimens/fallocate shims, Linux procfs for dentry stats, and global verify/maximize/minimize flags. Options are `dentries` and `dentry-order`.

## Risks
High dentry counts can exhaust filesystem space, inode limits, or directory performance. Verify mode adds reads and can fail if files were not written fully. Random order maps to one of the deterministic orders for each unlink batch, so it is not fully shuffled. `stress_dentry_misc()` intentionally calls invalid operations on directories; those should stay best-effort. Cleanup must remove files even after partial creation or `ENOSPC`.

## Test Signals
Signals include clean temp directory removal, no read verification errors, metrics for all four operation classes, correct handling of `ENOSPC`, and useful dentry allocation logs on Linux. Filesystem-specific testing should cover tmpfs, ext4/xfs, and constrained inode/free-space environments.
