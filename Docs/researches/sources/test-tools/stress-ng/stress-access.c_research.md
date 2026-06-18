# sources/test-tools/stress-ng/stress-access.c

## Purpose
`stress-access.c` implements the `access` stressor, exercising `access`, `faccessat`, `faccessat2`, `chmod`, and `fchmod` under concurrent permission changes.

## Important APIs, Types, And Functions
The stressor entry is `stress_access`, registered through `stress_access_info`. `stress_access_spawn` forks two lower-priority child loops that chmod and access a shared file. `stress_access_reap` kills/waits children. `shim_faccessat` prefers `faccessat2` or the raw syscall when available. Static `modes` maps chmod modes to access modes; `access_flags` probes multiple `faccessat` flags.

## Control Flow
The parent creates a temp directory and two files, mmaps shared PID records and metrics, spawns two child stressors, synchronizes start, and then loops over permission modes. For each mode it sets permissions, verifies expected access success or failure, exercises `faccessat` flags and bad descriptors, and increments bogo ops. Children concurrently mutate and query the second file, updating shared metrics. Cleanup kills children, restores file modes, closes/unlinks files, removes the temp directory, and unmaps shared memory.

## State And Persistence
Temporary filesystem state includes two files and a temp directory. Shared anonymous mmap state holds child PID records and metrics. The global static `metrics` pointer is used by children after fork. No persistent files should remain after normal cleanup.

## Dependencies And Integration Points
It depends on capability checks for root semantics, temp-file helpers, filesystem type detection, `core-sync`, `core-mmap`, `core-killpid`, and access/faccessat syscalls. It is registered as `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

## Risks
Permission semantics vary by filesystem and root privileges; the code suppresses chmod/access failure reporting on exfat, msdos, hfs, and fuse. Concurrent chmod/access can race by design, so metrics and expected outcomes must be interpreted carefully. Child cleanup must run on all error paths to avoid leaked workers.

## Test Signals
`--access` with verification is a direct signal. Debian `fast-test-all` runs it, and kernel coverage exercises filesystem variants that can expose permission semantic differences.
