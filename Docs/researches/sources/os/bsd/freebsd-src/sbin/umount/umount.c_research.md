# File Research: sources/os/bsd/freebsd-src/sbin/umount/umount.c

## Purpose
Implements the `umount` command, including individual unmounts, fstab-driven unmount-all, mount-table unmount-all, NFS cleanup RPCs, and optional md-device detach.

## Main Elements
- `main()` parses `-a`, `-A`, `-d`, `-F`, `-f`, `-h`, `-N`, `-n`, `-t`, and `-v`.
- Enforces incompatible combinations such as `-f` with `-n`, and validates `-N` forced NFS dismount use.
- `umountall()` recursively processes fstab entries so unmounts happen in reverse order while skipping root and non-mount fstab types.
- `checkname()` resolves input as fsid, mountpoint, source device, path with trailing slashes removed, deprecated NFS `host@path`, or `statfs()` fallback.
- `umountfs()` prefers unmount by fsid, falls back to path for old kernels, marks internal mount-cache entries removed, and prints verbose output.
- NFS handling detects host/path, filters by `-h`, suppresses MOUNTPROC_UMNT for NFSv4, selects tcp/udp from mount options, updates `/var/db/mounttab`, and supports `nfssvc(NFSSVC_FORCEDISM)`.
- `md_detach()` detaches backing `md(4)` devices after unmount when `-d` is set.

## Dependencies And Integration
Uses `getfsstat`, `unmount(2)`, fstab APIs, VFS type filtering helpers, NFS RPC/mount protocols, `nfssvc`, mounttab helpers, and md ioctl interfaces.

## Risk Notes
Unmount ordering and mount identity resolution are correctness-critical. NFS RPC cleanup only occurs when this is the last matching mount and the operation is not forced.
