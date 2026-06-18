# File Research: sources/os/bsd/freebsd-src/sbin/mdmfs/mdmfs.c

## Summary
Implements `mdmfs`, a wrapper around `mdconfig`, `newfs`, `mount`, optional `tmpfs`, mountpoint ownership/mode setup, and skeleton-directory copying. It emulates deprecated `mount_mfs` command-line behavior.

## Main Responsibilities
- Parses mount_mfs-compatible options and translates many of them into `mdconfig`, `newfs`, or `mount` arguments.
- Selects tmpfs automatically for `auto` when available and when multilabel MAC is not requested.
- Creates md devices with fixed or automatic units, formats them unless `-P` is used, then mounts them.
- Supports vnode, malloc, and swap-backed md devices.
- Converts size arguments using mdconfig semantics, including unsuffixed 512-byte block counts.
- Applies mountpoint mode, uid, and gid after mount when requested.
- Optionally copies a skeleton tree into the mounted filesystem with `pax`.

## Key Functions
- `argappend()`: appends formatted helper arguments.
- `run()`: forks and execs helper programs from a whitespace-split command string.
- `do_mdconfig_attach()` / `do_mdconfig_attach_au()` / `do_mdconfig_detach()`.
- `do_newfs()`, `do_mount_md()`, `do_mount_tmpfs()`.
- `do_mtptsetup()`: chmod/chown after mount, skipping read-only mounts.
- `extract_ugid()`: parses `user:group`.

## Dependencies And Integration
Uses `/sbin/mdconfig`, `/sbin/newfs`, `/sbin/mount`, `/bin/pax`, md(4) type constants, `statfs`, user/group databases, and kld module lookup/loading for tmpfs.

## Research Notes
`run()` does not implement shell quoting; it splits generated command strings on spaces before `execv`. Paths or option values containing spaces are therefore fragile. This is consistent with older wrapper-style code but important for behavior analysis.
