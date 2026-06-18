# sources/test-tools/stress-ng/stress-ramfs.c research

Purpose: implements `ramfs`, a privileged Linux stressor that repeatedly mounts ram-backed filesystems, exercises basic filesystem operations, optionally fills them, and unmounts with retry/error probes.

Important APIs, types, and functions: `stress_ramfs_supported()` requires `CAP_SYS_ADMIN`. `stress_ramfs_umount()` retries `umount`/`umount2(MNT_FORCE)` and then exercises invalid unmount calls. `stress_ramfs_fs_ops()` creates, stats, optionally fallocates/writes/fsyncs, symlinks, unlinks, mkdirs, and rmdirs inside the mount. `stress_ramfs_child()` performs mount cycles using modern `fsopen`/`fsconfig`/`fsmount`/`move_mount` when available or classic `mount()`.

Control flow: parent `stress_ramfs_mount()` synchronizes and repeatedly forks a child. The child creates a stress-ng temp directory, resolves it, alternates `ramfs` and `tmpfs`, mounts with size options, runs filesystem operations, unmounts, and increments bogo ops until stopped. Parent waits, treats OOM-like `SIGKILL` as restartable, and propagates failure/no-resource statuses.

State and persistence: uses a temporary directory as mountpoint and kernel mount namespace state. Cleanup aggressively unmounts and removes the temp directory; no files should persist.

Dependencies and integration: Linux-only with clone namespace macros and mount APIs; uses stress-ng capabilities, temp-dir helpers, signal handlers, fork retry, and scheduler settings. Classified as OS and `VERIFY_ALWAYS`.

Risks: requires mount privileges and can consume memory, especially with `ramfs-fill` or aggressive mode. Mount cleanup is critical; failures could leave mounts if the process is killed outside the cleanup path. OOM behavior is expected and partially handled.

Test signals: capability skip, mount/no-resource skip, filesystem operation failures, OOM restart debug, bogo count per mount cycle, and absence of leftover mountpoints.
