# File Research: sources/os/linux/linux/fs/proc_namespace.c

## Role

Implements `/proc/<pid>/mounts`, `/proc/<pid>/mountinfo`, and `/proc/<pid>/mountstats`. It is procfs-facing code that depends closely on mount namespace internals.

## Key Functions

- `mounts_open_common()` obtains the target task, pins its mount namespace and fs root, opens a private seq file, and stores a `proc_mounts` context.
- `mounts_release()` drops the pinned root path and mount namespace.
- `show_vfsmnt()` emits traditional `/proc/mounts` lines.
- `show_mountinfo()` emits mountinfo records including mount IDs, parent IDs, root path, mount path, propagation tags, filesystem type, source, and options.
- `show_vfsstat()` emits mountstats records and delegates optional filesystem stats to `sb->s_op->show_stats`.
- `mounts_poll()` reports namespace event changes through poll using `ns->event`.

## Option Formatting

- `show_sb_opts()` prints superblock options such as `sync`, `dirsync`, `mand`, and `lazytime`, then delegates to LSM `security_sb_show_options()`.
- `show_vfsmnt_opts()` prints mount flags such as `nosuid`, `nodev`, `noexec`, `noatime`, `relatime`, `nosymfollow`, and `idmapped`.
- `mangle()` escapes whitespace, backslash, and `#` for proc output.
- `show_type()` prints filesystem type plus optional subtype.

## Exported Operations

- `proc_mounts_operations`
- `proc_mountinfo_operations`
- `proc_mountstats_operations`

All use seq reads and shared open/release helpers; mounts and mountinfo also support poll.

## Research Notes

The file is careful to present paths relative to the target task's root, returning `SEQ_SKIP` for mountpoints outside a chroot. It snapshots namespace/root references during open so iteration remains stable across task changes.
