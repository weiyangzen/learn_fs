<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cgroup.c -->
# sources/test-tools/stress-ng/stress-cgroup.c

## Purpose
Implements the `cgroup` stressor, which repeatedly mounts cgroup v2, reads and writes controller files, moves a child process into and out of a subgroup, and unmounts the hierarchy.

## Important APIs, Types, and Functions
`stress_cgroup_info` registers the stressor with a `supported` callback requiring `CAP_SYS_ADMIN`. `stress_cgroup_mount()` forks a child for mount work. `stress_cgroup_child()` creates a temp mount point and mounts cgroup2 using either the modern `fsopen`/`fsconfig`/`fsmount`/`move_mount` path or `mount()`. Helpers handle mount-state detection from `/proc/mounts`, retrying unmounts, reading files, enabling controllers, and manipulating `cgroup.procs`.

## Control Flow
The parent synchronizes, forks a mount child, waits for completion, and restarts if the child appears OOM-killed. The child creates a realpath temp directory, mounts cgroup2, updates subtree controls, reads standard cgroup files, creates a `stress-ng-PID` subgroup with a busy child process, iterates a large table of controller values to read/write, then unmounts with retries and removes the temp directory.

## State and Persistence Behavior
State is temporary but privileged: a cgroup2 mount, subgroup directory, controller file writes, a forked workload process, and a temp directory. Cleanup attempts forced or repeated unmounts and directory removal. No intended persistent repository state is written.

## Dependencies and Integration Points
Depends on Linux cgroup v2, mount APIs, CAP_SYS_ADMIN, stress-ng temp filesystem helpers, file read/write helpers, process kill/wait helpers, scheduling, and memory-pressure helpers. Integrates with stress-ng support checks so it is skipped without privileges.

## Risks and Edge Cases
This stressor can affect kernel cgroup state and can trigger OOM conditions. Mount and unmount races require retry logic. Controllers vary by kernel configuration, so many reads/writes intentionally ignore failure. Cleanup failures can leave a mounted temp path if the kernel refuses unmount. Running without CAP_SYS_ADMIN skips.

## Test Signals
Useful signals include clean skip without privileges, successful mount/read/write/unmount cycles with bogo increments when privileged, no lingering mount at the temp realpath, and expected debug retry counts instead of fatal failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cgroup.c -->
