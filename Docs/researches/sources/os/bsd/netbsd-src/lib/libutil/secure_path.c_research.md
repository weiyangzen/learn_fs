# File Research: sources/os/bsd/netbsd-src/lib/libutil/secure_path.c

## Purpose
Checks whether a path is safe for privileged use.

## Key Details
- Uses `lstat`.
- Requires a regular file.
- Requires root ownership.
- Rejects group- or world-writable files.
- Logs problems through syslog.
- Returns `0` for secure, `-1` otherwise.

## Dependencies and Role
- Used by `login_cap.c` and `getbootfile.c`.
- Security-sensitive filesystem metadata validation.
