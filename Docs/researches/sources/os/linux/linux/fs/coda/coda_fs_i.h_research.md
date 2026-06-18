# File Research: sources/os/linux/linux/fs/coda/coda_fs_i.h

Coda inode-private and file-private structure definitions.

Defines:
- `struct coda_inode_info`: Coda FID, flags, mmap count, cached permission epoch/fsuid/mask, spinlock, and embedded VFS inode.
- `CODA_MAGIC`: magic value for file private data validation.
- `struct coda_file_info`: magic, host/container file, mmap count, and access-intent support flag.
- Inode flags: `C_VATTR`, `C_FLUSH`, `C_DYING`, `C_PURGE`.

Declared helpers:
- `coda_cnode_make()`
- `coda_iget()`
- `coda_cnode_makectl()`
- `coda_fid_to_inode()`
- `coda_ftoc()`
- `coda_replace_fid()`

Concurrency contract:
- Header comment states `c_lock` protects flags, map count, permission epoch, cached uid, and cached permission mask.
- `vfs_inode` is set only at creation.
- `c_fid` is intended immutable except for the documented replacement special case.
