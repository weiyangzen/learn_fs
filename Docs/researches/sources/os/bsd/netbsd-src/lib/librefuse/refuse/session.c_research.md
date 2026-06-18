# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/session.c

This file implements a minimal FUSE session API by treating `struct fuse_session *` as identical to `struct fuse *`. It returns the session pointer, exposes `puffs_getselectable(fuse->pu)` as the session fd, and forwards signal handler installation/removal to ReFUSE internals.

Integration points: used by FUSE 2.5+ signal/session-facing APIs. Risk is semantic mismatch: the fd is `/dev/puffs` selectable state, not a Linux `/dev/fuse` fd, so consumers must not assume Linux kernel protocol behavior.
