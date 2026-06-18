# File Research: sources/local-fs/xfsprogs/libxfs/inode.c

Userspace inode allocation, loading, flushing, metadata-inode lookup, release, and ownership initialization helpers.

Key responsibilities:
- Creates newly allocated in-core inodes with `libxfs_icreate`.
- Flushes dirty in-core inode state to an inode buffer with verifier and CRC updates.
- Implements a minimal `libxfs_iget` that allocates an inode, maps it, and reads ondisk state unless a new V3 inode can be initialized directly.
- Validates and loads metadata files with expected file mode/metatype.
- Releases inode fork memory and frees in-core inode objects.
- Provides `inode_init_owner` behavior for uid/gid/mode inheritance.

Important behavior:
- New V3 non-ikeep inodes get a random generation without reading disk.
- Local data and attr forks are verified before inode flush.
- Metadata-directory files must be marked as metadir inodes with matching metatype.
- No persistent inode cache lookup is implemented; objects are allocated per `iget`.

Dependencies:
- Uses inode buffer, fork, bmap, transaction, allocation, directory, metadir, and random helpers.

Notable risks:
- Assertions enforce fork extent/nblock invariants before flush.
- Minimal userspace cache means callers must manage inode lifetime carefully.
