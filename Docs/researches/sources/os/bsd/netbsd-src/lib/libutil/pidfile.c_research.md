# File Research: sources/os/bsd/netbsd-src/lib/libutil/pidfile.c

## Purpose
Creates, locks, reads, cleans, and tracks daemon pidfiles.

## Key Details
- Maintains process-global `pf_fd`, `pf_path`, and removability state.
- `pidfile_lock` opens and locks the pidfile, writes current PID, and registers `atexit` cleanup once.
- Supports default `/var/run/<progname>.pid` or `/var/run/<name>.pid` construction.
- Uses `O_CLOEXEC` and `O_EXLOCK` when available, with fallback `fcntl`/`flock`.
- If locked by another process, attempts to read and return that PID.
- `pidfile_clean` verifies the pidfile still contains this process’s PID before truncating/unlinking.
- `pidfile_unremoveable` prevents unlink while still truncating and unlocking.

## Dependencies and Role
- Daemon lifecycle helper.
- Filesystem behavior matters for lock persistence and cleanup after privilege or chroot changes.
