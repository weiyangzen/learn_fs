# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/opdump.c

This file contains debug pretty-printers for puffs request and response frames. It defines reverse maps for VFS operations, vnode operations, cache operations, error notifications, and flush operations, plus exported counts for the public `puffsdump.h` debug interface.

`puffsdump_req` prints request id, operation class, whether a reply is expected, operation type name, cookie, auxiliary buffer address/length, process id, and LWP id. For vnode operations it dispatches to specialized dump functions for lookup, read/write, open, target-cookie operations, readdir, create-like operations, and setattr. It also prints elapsed wall-clock time since the previous call under the global puffs lock.

`puffsdump_rv` prints operation-specific response fields for lookup, create-like operations, read/write, readdir, and getattr, followed by the request result and strerror text. The internal `dumpattr` routine formats `struct vattr` while suppressing `PUFFS_VNOVAL` fields as `NOVAL`, covering type, mode, link count, uid/gid, fsid, inode, size, block size, timestamps, generation, flags, rdev, bytes, filerev, and vaflags.

The remaining helpers print cookies, component names, lookup results, create results, read/write offsets and residuals, readdir offsets/residual/eof, open mode, target cookie, and attributes. The file is intentionally debug-only and contains comments acknowledging type punning between similar puffs message layouts.
