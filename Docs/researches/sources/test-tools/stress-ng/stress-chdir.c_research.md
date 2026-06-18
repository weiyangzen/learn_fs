<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chdir.c -->
# sources/test-tools/stress-ng/stress-chdir.c

## Purpose
Implements the `chdir` stressor, which creates many temporary directories and repeatedly exercises `chdir()` and `fchdir()` success and failure paths.

## Important APIs, Types, and Functions
`stress_chdir_info` registers options including `chdir-dirs`. `stress_chdir_info_t` stores each generated path, open directory fd, and mkdir status. The main `stress_chdir()` function handles directory creation, open fd collection, permission-denial probing, invalid path tests, cleanup, and the "chdir calls per sec" metric.

## Control Flow
The stressor chooses directory count from settings or minimize/maximize flags, allocates metadata, records the original cwd, creates a stress-ng temp directory, populates many child directories, then synchronizes. The run loop changes into each created path, randomly `fchdir()`s to another directory fd, changes to `/`, optionally removes permissions and probes access failure for non-root, returns to the original cwd, and then probes bad, non-directory, invalid-fd, empty, and overlong path cases.

## State and Persistence Behavior
Creates up to `chdir-dirs` temporary directories and holds open fds to them. It must always restore the original cwd before cleanup. Cleanup closes fds, removes each created directory, removes the temp root, frees path strings, and emits a tidy message if removal takes long.

## Dependencies and Integration Points
Depends on stress-ng temp filesystem helpers, capability checks for root, random generation, metrics, filesystem diagnostics, and option parsing. It integrates with stress-ng minimize/maximize behavior for resource scaling.

## Risks and Edge Cases
Large directory counts can hit memory, inode, link-count, or disk-space limits. Failing to restore cwd would break cleanup and later stressors. Permission-denial checks are skipped for root because root may bypass access mode. Concurrent filesystem pressure can cause ENOMEM/ENOSPC/EMLINK paths.

## Test Signals
Good signals include successful cleanup of all generated directories, nonzero chdir-rate metric, correct skip/no-resource behavior under low resources, and no unexpected failures for known invalid path probes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chdir.c -->
