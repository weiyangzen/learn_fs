# File Research: sources/os/bsd/freebsd-src/sbin/mount_fusefs/mount_fusefs.c

## Summary
Mount helper for FUSE filesystems. It parses FUSE-specific options, opens or validates a fuse device/file descriptor, optionally launches a FUSE daemon, and passes the device fd to the kernel via `nmount()`.

## Main Responsibilities
- Parses positional arguments flexibly, plus long options such as `--daemon`, `--daemon_opts`, `--special`, and `--mountpath`.
- Translates FUSE options into mount flags and iovecs, including `allow_other`, `default_permissions`, `max_read`, `subtype`, `fsname`, `automounted`, `intr`, and `auto_unmount`.
- Ignores selected Linux-specific options for compatibility.
- Supports safe mode that forbids spawning daemons.
- Opens `/dev/fuse` or accepts a numeric fd.
- Validates that the device is a fuse character device.
- Sets `FUSE_DEV_FD` and `FUSE_NO_MOUNT` before launching daemon code.
- Calls `nmount()` with `fstype=fusefs`, `fspath`, `from`, and `fd`.

## Dependencies And Integration
Uses `getopt_long`, `getmntopts`, `devname_r`, environment variables expected by FUSE daemons, and FreeBSD `nmount()`.

## Research Notes
`--daemon` execution uses `system()` with a constructed background command string, while the positional daemon path uses `fork()` plus `execvp()`. Safe mode blocks both daemon-spawning surfaces.
