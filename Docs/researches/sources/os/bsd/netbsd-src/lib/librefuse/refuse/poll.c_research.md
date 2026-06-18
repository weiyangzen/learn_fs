# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/poll.c

This file provides stubs for the FUSE poll notification API. `fuse_notify_poll` returns success and `fuse_pollhandle_destroy` does nothing.

The comment states ReFUSE does not implement `puffs_node_poll` and therefore will never invoke `fuse_operations.poll`. These functions exist only for API compatibility. Risk is that filesystems relying on real poll notification semantics will silently get no behavior.
