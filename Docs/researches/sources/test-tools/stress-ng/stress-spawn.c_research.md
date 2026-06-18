# sources/test-tools/stress-ng/stress-spawn.c

## Purpose

`stress-spawn.c` implements `spawn`, a scheduler/OS stressor that repeatedly starts the current stress-ng executable using `posix_spawn()` and waits for it to exit. The spawned child is invoked with `--exec-exit`, so the workload measures process creation and image setup without running another full stress workload.

## Important APIs, Types, and Functions

- `stress_spawn_supported()` prevents running the stressor as root, avoiding accidental privileged spawning of another executable.
- `stress_spawn()` obtains `LD_LIBRARY_PATH` environment setup, resolves the current executable with `stress_proc_self_exe_get()`, builds `argv_new` as `{ path, "--exec-exit", NULL }`, repeatedly calls `posix_spawn()`, waits with `shim_waitpid()`, counts failures, and optionally fails verification if any spawn failed.
- `stress_spawn_info` registers the stressor with `CLASS_SCHEDULER | CLASS_OS` and `VERIFY_OPTIONAL`.

## Control Flow

Both the supported callback and the entry point reject effective UID zero. The entry point builds a minimal environment containing the current library-path variable returned by `stress_env_ld_library_path_get()`, resolves the running executable path, synchronizes start, and enters the run loop. Each iteration increments the attempted spawn count, calls `posix_spawn()`, logs and counts spawn-call failures, or waits for the child and increments bogo operations. Exited child statuses other than `EXIT_SUCCESS` are counted as spawn failures. On exit it frees the library-path string and, under `--verify`, reports and fails if any failures occurred.

## State and Persistence Behavior

The stressor creates only transient child processes. Static `argv_new` and `env_new` arrays are mutated with the resolved executable and optional environment string. It writes no files and leaves no persistent state.

## Dependencies and Integration Points

The file requires `spawn.h` and `posix_spawn()`. It uses stress-ng helpers for current executable discovery, environment construction, synchronization, waitpid, bogo accounting, option flags, and logging. Unsupported builds export `stress_unimplemented`.

## Risks and Edge Cases

The root guard is deliberate because the executable path comes from the running process and should not be repeatedly spawned with elevated privileges in this test. Failure to resolve `/proc/self/exe` or platform equivalent yields `EXIT_NOT_IMPLEMENTED`. `env_new[0]` can be NULL, which is acceptable for an empty environment array. Spawn failures are tolerated unless verification is enabled, making this suitable for resource-pressure runs.

## Test Signals

A non-root run should repeatedly spawn stress-ng with `--exec-exit`, increment bogo operations, and exit success when children exit cleanly. Root runs should skip or fail early. Verification runs should report a failure percentage when child exits or spawn calls fail.
