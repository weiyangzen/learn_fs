# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse_signals.c

Read completely: 331 lines.

Implements ReFUSE signal handler registration/removal for FUSE-compatible filesystems. It tracks all `struct fuse *` instances that requested signal handling in a process-global linked list, installs shared handlers for `SIGHUP`, `SIGINT`, and `SIGTERM`, and ignores `SIGPIPE` only when the previous action was default.

The exit handler calls `fuse_exit()` for every tracked filesystem, then chains to the previously installed handler if it was neither default nor ignored. In `MULTITHREADED_REFUSE` builds, it uses a global mutex and temporarily blocks the handled signals while mutating handler/list state.

Removal deletes the matching fuse instance and restores the saved signal actions only after the last tracked instance is gone. Notable risks are deliberate signal-safety compromises: the handler may take a pthread mutex and call non-async-signal-safe code, relying on the signal-blocking discipline around list changes.
