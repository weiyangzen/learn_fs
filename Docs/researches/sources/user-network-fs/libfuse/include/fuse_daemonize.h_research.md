# sources/user-network-fs/libfuse/include/fuse_daemonize.h

`fuse_daemonize.h` exposes the newer early daemonization API used when mount setup and `FUSE_INIT` synchronization require explicit parent/child handshaking. It supplements the older `fuse_daemonize(int foreground)` declaration in `fuse_common.h`.

The public flags are `FUSE_DAEMONIZE_NO_CHDIR` and `FUSE_DAEMONIZE_NO_BACKGROUND`. The functions are `fuse_daemonize_early_start`, `fuse_daemonize_early_success`, `fuse_daemonize_early_fail`, and `fuse_daemonize_early_is_active`. A filesystem calls early start before `fuse_session_mount`; the parent waits while the child mounts and later signals success or failure. For sync `FUSE_INIT`, success/failure belongs after mount and before the loop; async init can signal from the init callback.

State is process-level daemonization activity and the parent/child synchronization channel. Integration points are `fuse_session_mount`, `fuse_session_loop*`, `fuse_session_set_sync_init`, and foreground/background command-line handling.

Risks include hanging the parent by missing success/failure, reporting success before the mount is usable, incorrect cwd/background behavior, and unsafe `fork()` timing with sync init or io-uring. Test signals include foreground and background modes, no-chdir, child failure propagation, success after sync mount, async init signaling, double signal calls, and inactive cleanup.
