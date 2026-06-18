# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_status.c

## Purpose

Implements `/proc/<pid>/status` and `/proc/<pid>/cmdline`.

## Main Entry Points

`procfs_doprocstatus()` emits a single status line containing:
- escaped command name.
- pid, parent pid, process group, session id.
- controlling tty and session flags.
- process start time, user CPU time, system CPU time.
- first thread wait message.
- effective/real uid and gid plus supplementary groups.
- jail/prison name or `-`.

It locks the process, session, first thread, and process stats as needed while gathering fields.

`procfs_doproccmdline()`:
- returns cached `p_args` contents when present and visible to the caller.
- returns an empty result for system processes.
- otherwise calls `proc_getargv()` to read argv from process memory.
- deliberately avoids falling back to `p_comm` if argv is unavailable.

## Integration Points

Registered by `procfs.c` as `status` and `cmdline`, both read-only.

## Risks and Review Notes

`status` produces historical procfs formatting, including comma-separated group data and escaped command bytes. `cmdline` follows Linux-like zero-length behavior when argv is unavailable, which callers must distinguish from an error-free empty command line.
