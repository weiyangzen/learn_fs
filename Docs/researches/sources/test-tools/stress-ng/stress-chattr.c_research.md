<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chattr.c -->
# sources/test-tools/stress-ng/stress-chattr.c

## Purpose
Implements the Linux `chattr` stressor, exercising ext-style inode attribute get/set ioctls over individual flags and generated flag permutations on a shared temporary file.

## Important APIs, Types, and Functions
`stress_chattr_info` exposes the stressor on Linux or an unimplemented stub elsewhere. `stress_chattr_flag_t` maps EXT2/EXT3/EXT4/NOCOW flag bits to chattr-style characters. `do_chattr()` opens the file, allocates/mmap's a page, reads original flags with `SHIM_EXT2_IOC_GETFLAGS`, clears and sets flags with `SHIM_EXT2_IOC_SETFLAGS`, verifies selected flag subsets when single-instance, probes illegal flags, and uses a signal handler to survive mmap write faults.

## Control Flow
`stress_chattr()` installs SIGSEGV/SIGBUS handlers, builds the supported mask, computes flag permutations, creates a temp directory shared by worker instances, then loops through each known flag plus one permutation. Unsupported filesystems return `EXIT_NOT_IMPLEMENTED` after all attempts fail. It records successful flag-set rate as a metric and removes the file and directory.

## State and Persistence Behavior
Creates a temporary directory and shared file derived from the parent PID. It changes inode attributes and writes to a file-backed mapping but restores/clears flags and unlinks the file on each helper pass and at cleanup. Runtime signal state is held in `jmp_env` and `do_jmp`.

## Dependencies and Integration Points
Uses Linux `ioctl`, stress-ng temp file helpers, flag permutation helper, signal handling, mmap/fallocate wrappers, fsync/unlink wrappers, metrics, and filesystem-type diagnostics. Multiple stressor instances intentionally contend on the same file.

## Risks and Edge Cases
Filesystem support differs widely; EOPNOTSUPP, ENOTTY, EPERM, and EINVAL are expected. Immutable or append-only flags can interfere with writes and cleanup if not cleared. Mmap writes may fault under certain attributes. Concurrent workers can observe non-deterministic flags, so strict verification is limited to one instance.

## Test Signals
Expected signals include either a clear "not supported on filesystem" skip or nonzero "successful chattr flags set per sec". There should be no lingering temp file with restrictive attributes. Test on ext-family filesystems and a non-supporting filesystem such as tmpfs if available.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chattr.c -->
