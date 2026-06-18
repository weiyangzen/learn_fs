# File Research: sources/os/linux/linux-stable/fs/coda/coda_fs_i.h

## Purpose
Defines Coda per-inode and per-file private kernel data structures plus cnode helper prototypes.

## Main Contents
- `struct coda_inode_info`: Coda FID, flags, mmap count, cached permission epoch/fsuid/mask, spinlock, and embedded VFS inode.
- `struct coda_file_info`: magic value, Venus/container file pointer, mmap count, and access-intent support flag.
- Inode flags: `C_VATTR`, `C_FLUSH`, `C_DYING`, `C_PURGE`.
- Prototypes for cnode creation, lookup, control inode creation, FID replacement, and file-private access.

## Integration Points
Included by `coda_linux.h` and implementation files. It is the core state contract for directory, file, cache, inode, and psdev/upcall code.

## Risks And Review Focus
- `c_fid` is documented as immutable except for the special replacement path.
- `c_lock` protects flags, map count, and permission cache fields; callers must follow that boundary.
