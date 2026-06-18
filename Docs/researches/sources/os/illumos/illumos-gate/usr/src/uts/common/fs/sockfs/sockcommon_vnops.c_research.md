# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockcommon_vnops.c

## Purpose
Defines the vnode operations for sockfs socket vnodes.

## Main Behavior
- Registers vnode operations for open, close, read, write, ioctl, setfl, getattr, setattr, access, fsync, inactive, fid, seek, poll, and dispose.
- Open increments `so_count`; close decrements it and initiates socket close when the last open reference goes away.
- Read/write translate vnode I/O into `socket_recvmsg()` and `socket_sendmsg()` with a minimal `nmsghdr`; non-byte-stream writes set `MSG_EOR`.
- `socket_vop_setfl()` records `FNDELAY`/`FNONBLOCK` and handles BSD `FASYNC` compatibility through `FIOASYNC`.
- `socket_vop_getattr()` fabricates socket vnode attributes, including stable-ish 32-bit node IDs derived from the sonode pointer and STREAM/TPI timestamp behavior.
- `socket_vop_setattr()` updates atime/mtime/ctime only for STREAM/TPI sockets.
- Access checks delegate to the underlying STREAMS device for STREAM/TPI sockets and allow non-STREAM sockets.
- Fsync returns `EINVAL`, fid returns `EINVAL`, and seek returns `ESPIPE`.
- Inactive releases the vnode and destroys the underlying socket when the vnode count reaches zero.

## Integration Points
- `socket_vnodeops_template` is installed by sockfs setup and used by sonode construction.
- Calls `socket_close_internal()` and `socket_destroy_internal()` from `sockcommon.c`.
- Cooperates with `socktpi` for STREAM-mode sockets.

## Risks and Notes
- Attribute values are intentionally synthetic and do not affect filesystem nodes backing AF_UNIX pathnames.
- The node-id derivation is explicitly capped to 32 bits to avoid surprises for non-largefile-aware 32-bit processes.
- Close cleans locks, shares, and STREAM state before final socket teardown.
