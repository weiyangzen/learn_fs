# File Research: sources/virtualization/libguestfs/daemon/du.c

Wraps `du -s` for guest paths.

Key points:
- Converts guest path through `sysroot_path`.
- Runs `du -s <path>` with pulse-mode progress.
- Parses the leading integer from stdout as an `int64_t`.
- Reports parsing failure if command output does not start with a number.
