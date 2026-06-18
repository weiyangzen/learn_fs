<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bind-mount.c -->
# sources/test-tools/stress-ng/stress-bind-mount.c

Purpose: `stress-bind-mount.c` implements the Linux `bind-mount` stressor. It repeatedly bind-mounts `/bin` onto a temporary directory, stats files through the mounted view, unmounts, and records mount/unmount latency.

Important APIs/types/functions: the stressor is gated on Linux bind-mount flags, `clone()` namespace constants, and capability checks for `CAP_SYS_ADMIN`. `stress_bind_mount_supported()` skips without the capability. `stress_bind_mount_child_handler()` clears the continue flag on `SIGALRM` and exits for other signals. `stress_bind_mount_exercise()` performs the mount using either modern `open_tree()`/`move_mount()` or legacy `mount(MS_BIND | MS_REC)`, validates visibility by comparing `lstat()` success under `/bin` and the bind target, retries `umount2(MNT_DETACH)` or `umount()`, and records metrics.

Control flow: `stress_bind_mount()` syncs, creates a temporary mount point, and repeatedly calls `stress_bind_mount_exercise()` until the stressor stops or an exercise fails. The exercise function installs handlers, sets a parent-death alarm, attempts one mount/unmount cycle per loop, increments bogo operations after unmount, and removes the path as a child-side safety cleanup.

State and persistence behavior: persistent state is a temporary directory and a transient mount. The directory is removed in both exercise and top-level cleanup. Mount state should be detached each iteration; stale mounts are the main persistence risk.

Dependencies and integration points: depends on stress-ng capability helpers, temp path helpers, filesystem stat helpers, signal wrappers, process-state transitions, and metrics. It is classified as filesystem, OS, and pathological, with `VERIFY_ALWAYS`.

Risks: requires elevated privilege and mutates mount namespace state. The compile-time gate mentions user/mount namespace clone constants but the code itself does not create a new namespace here, so running in the caller's namespace can be dangerous if cleanup fails. It assumes `/bin` exists and is suitable as the bind source.

Test signals: run with and without `CAP_SYS_ADMIN`, with `open_tree`/`move_mount` available and unavailable, on systems without `/bin`, and under forced `ENOSPC`, `EACCES`, or `ENOENT`. Metrics are `microsecs per mount` and `microsecs per umount`; stat failures across the bind target are reported.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bind-mount.c -->
