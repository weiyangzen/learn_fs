# File Research: sources/os/bsd/netbsd-src/sys/fs/nilfs/nilfs_mount.h

This public header defines the NILFS mount argument ABI. `NILFSMNT_VERSION` is `1`, and `struct nilfs_args` carries the version, filesystem specifier path, NILFS mount flags, timezone offset, checkpoint number, and reserved expansion space.

Integration points: installed through the NILFS makefile and consumed by mount tooling and kernel mount code. The checkpoint number supports mounting a checkpoint/snapshot view rather than only the live head.

Risks: this is a user/kernel ABI structure. Field ordering, integer widths, pointer handling, and the reserved bytes should remain stable across versions. `NILFSMNT_BITS` is currently empty, so any future mount flags need coordinated definition and decoding.
