# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_mount.h

## Purpose
Defines the userland-to-kernel mount argument structure and mount flags for HAMMER2.

## Public Interface
`struct hammer2_mount_info` contains:
- `const char *volume`: user pointer to a device/label string formatted like `/dev/ad0s1a@LABEL`.
- `int hflags`: extended HAMMER2 mount flags.
- `int cluster_fd`: socket/pipe fd for cluster management.
- reserved padding.

Flags:
- `HMNT2_LOCAL`: force local mode, disassociating PFSs from their clusters, mainly for debugging.
- `HMNT2_EMERG`: emergency mode.
- `HMNT2_UNUSED01`: reserved/unused.
- `HMNT2_USERFLAGS` and `HMNT2_DEVFLAGS` currently allow only `HMNT2_LOCAL`.

## Integration Notes
`hammer2_vfs_mount()` copies this struct from userland for non-root mounts, parses `volume`, applies PFS/device flags, and optionally holds `cluster_fd` for cluster reconnect. The header is also included by the ioctl ABI header.
