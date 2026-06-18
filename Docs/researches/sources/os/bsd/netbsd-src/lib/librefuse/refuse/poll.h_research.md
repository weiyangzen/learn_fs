# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/poll.h

This header declares the FUSE 2.8 polling API surface: opaque `struct fuse_pollhandle`, `fuse_notify_poll`, and `fuse_pollhandle_destroy`. It is inclusion-guarded for use through `<fuse.h>`.

Integration points: operation table headers from FUSE 2.8 onward include poll callback fields using this type. The declared API is mostly compatibility-only because `poll.c` does not implement real readiness notification.
