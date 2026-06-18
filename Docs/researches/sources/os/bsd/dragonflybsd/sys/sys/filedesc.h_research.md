# File Research: sources/os/bsd/dragonflybsd/sys/sys/filedesc.h

`filedesc.h` defines kernel file descriptor table structures and descriptor-management APIs. It sets `NDFILE` to 15 built-in descriptors and `NTDCACHEFD` for per-thread fd cache slots.

`struct fdnode` records a file pointer, per-fd flags, occupancy/reservation/subtree metadata, and per-thread caches. `struct filedesc` tracks descriptor arrays, current/root/jail directories as both vnode and namecache handles, file table sizing and high-water state, umask, references, close counters, spinlock, and built-in fd nodes.

It also defines `filedesc_to_leader` for POSIX lock ownership tracking across shared descriptor tables, close-on-exec/fork flags, `struct sigio`, duplication flags, and many kernel routines for allocation, copying, sharing, closing, revoking, holding, and signal-owner management.
