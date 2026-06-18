# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/puffsdump.h

This debug-only public header exposes puffs operation dump helpers implemented by `opdump.c`. Its comment warns callers outside libpuffs that the interfaces are intended only for debug builds and are not stable.

It includes the puffs kernel message-interface header and declares top-level request and response dump functions, cookie and component-name dump functions, operation-specific dump helpers for read/write, readdir, lookup, create, open, attributes, and target cookies.

It also exports the reverse-map arrays and counts for VFS operations, vnode operations, error notifications, and flush operations. These arrays let debug code translate numeric operation classes/types into readable names without duplicating libpuffs internals.
