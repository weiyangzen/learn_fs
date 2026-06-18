# File Research: sources/os/bsd/netbsd-src/lib/libutil/pidlock.c

## Purpose
Implements PID lock files and tty lock helpers.

## Key Details
- Creates a temporary file containing PID, optional hostname, and optional info.
- Atomically links it to the requested lockfile.
- If lock exists, reads owner PID and optionally hostname.
- Removes stale locks when the owning process no longer exists.
- Supports nonblocking mode via `PIDLOCK_NONBLOCK`.
- `ttylock` and `ttyunlock` build `/var/spool/lock/LCK..<tty>` paths after verifying `/dev/<tty>` exists and is character device.

## Dependencies and Role
- Locking helper for tty/device coordination.
- Uses hard-link semantics for atomicity, including NFS st_nlink verification.
