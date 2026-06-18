# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/chan.h

This internal header declares the opaque `struct fuse_chan` and hidden channel-management helpers used by version compatibility code. It is guarded against direct inclusion except through `<fuse.h>`.

Integration points: used by `v11.c`, `v21.c`, `v25.c`, and `v26.c` to emulate pre-FUSE-3 mount-before-new flows. Risks are hidden ABI coupling and global channel lifetime semantics.
