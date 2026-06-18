<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chmod.c -->
# sources/test-tools/stress-ng/stress-chmod.c

## Purpose
Implements the `chmod` stressor, repeatedly changing permission and special mode bits on a shared temporary file via `fchmod`, `chmod`, `fchmodat`, and `fchmodat2` paths.

## Important APIs, Types, and Functions
`stress_chmod_info` registers the stressor. The `modes[]` table is compiled from available `S_ISUID`, `S_ISGID`, sticky, and read/write/execute bits. `stress_chmod_check()` filters expected race or platform errors. `do_fchmod()` exercises fd-based mode changes plus an invalid fd. `do_chmod()` applies mode permutations and path-based variants including directory-fd calls and invalid path probes.

## Control Flow
`stress_chmod()` builds the full mode mask and permutations, creates a shared temp directory and file, opens the directory for `*at` calls, synchronizes workers, and loops through incremental masks over all modes. Each iteration calls fd and path variants, fsyncs the file, and increments bogo operations. Cleanup restores permissive mode, closes fds, unlinks the file, removes the directory, and frees permutations.

## State and Persistence Behavior
All state is temporary: one shared file per parent PID, one temp directory, one file fd, one directory fd, generated long path string, and mode permutation storage. No persistent state is intended after cleanup.

## Dependencies and Integration Points
Uses stress-ng temp path helpers, bad-fd helper, flag permutation helper, basename handling, shim wrappers for newer syscalls, metrics through bogo operations, and filesystem diagnostics. Multiple worker instances intentionally share the same target file.

## Risks and Edge Cases
Concurrent workers can remove or race on the same file, so ENOENT and ENOTDIR are treated as benign. Some platforms lack `fchmodat2` or have filesystem-specific errors such as EFTYPE. Large permutation sets add syscall volume. Cleanup must reset permissions before unlinking.

## Test Signals
Expected signals are sustained bogo operations, no unexpected chmod/fchmod errors, successful removal of the shared file, and coverage on systems both with and without native `fchmodat2`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chmod.c -->
