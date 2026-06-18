# File Research: sources/teaching/minix/minix/fs/mfs/inode.h

`inode.h` defines the in-core MFS inode table and associated cache lists. The first fields mirror on-disk V2/V3 inode data: mode, link count, uid/gid, size, timestamps, and ten zone pointers. The remaining fields are memory-only metadata: device, inode number, reference count, zone layout parameters, superblock pointer, dirty state, allocation search hint, last directory search position, mountpoint flag, seek/read-ahead flag, pending timestamp-update bits, hash links, and unused-list links.

The file defines `inode[NR_INODES]`, the unused tail queue, the inode hash bucket array, and hit/miss counters under the `EXTERN` mechanism. It also defines `NO_SEEK`/`ISEEK` and dirty-state macros. `IN_MARKDIRTY` mirrors buffer dirtying by warning and stack-tracing if code attempts to dirty an inode on a read-only superblock.
