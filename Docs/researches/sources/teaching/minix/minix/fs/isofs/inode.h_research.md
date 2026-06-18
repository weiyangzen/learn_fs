# File Research: sources/teaching/minix/minix/fs/isofs/inode.h

This header defines ISO9660 and Rock Ridge inode-related structures.

Structures:
- `struct iso9660_dir_record`: packed ISO directory record.
- `struct rrii_dir_record`: temporary Rock Ridge record with timestamps, mode, uid/gid, device, alternate name, symlink target, and reparented inode.
- `struct dir_extent`: contiguous logical-sector extent chain.
- `struct inode_dir_entry`: directory entry wrapper with inode pointer and ISO/Rock Ridge names.
- `struct inode`: in-memory inode with reference counts, mountpoint flag, `struct stat`, first extent, cached directory contents, symlink name, and skip flag.
- `struct opt`: currently only `norock`.

Constants:
- Directory flag masks `D_DIRECTORY`, `D_NOT_LAST_EXTENT`, `D_TYPE`.

Role:
- Defines the read-only isofs metadata model consumed by lookup, read, getdents, stat, and Rock Ridge parsing.
