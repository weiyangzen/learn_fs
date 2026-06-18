# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf_vfsops.c

DragonFly UDF VFS operations implementation: mount, unmount, root lookup, statfs, file-handle conversion, and vnode instantiation.

Key responsibilities:
- Registers `udf_vfsops` as a read-only local filesystem through `VFS_SET(..., VFCF_READONLY)` and module version 1.
- Implements `udf_mount`, requiring read-only mounts, rejecting root filesystem mounts, copying `struct udf_args`, supporting export updates, resolving the block device with namecache lookup, checking disk/read access, and delegating actual media parsing to `udf_mountfs`.
- Implements `udf_checktag`, validating descriptor tag id and checksum over descriptor-tag bytes except the checksum byte.
- Implements `udf_mountfs`, opening the device, allocating `struct udf_mnt`, initializing mount IDs/geometry defaults, reading the anchor at sector 256, scanning the main volume descriptor sequence for logical volume and partition descriptors, parsing partition maps, reading the file set descriptor, storing the root ICB, installing vnode ops, validating the root file entry, and initializing the vnode hash table.
- Implements `udf_unmount`, flushing vnodes, closing and releasing the device vnode, freeing sparing table/hash/mount allocations, and clearing mount state.
- Implements `udf_root`, resolving the root ICB into a vnode through `udf_vget` and marking it `VROOT`.
- Implements `udf_statfs`, reporting logical block size, partition length, zero free blocks/files, and mount source name.
- Implements `udf_vget`, using the vnode hash cache first, reading and copying a one-block UDF file entry, allocating a vnode, linking `udf_node` state, inserting it into the hash, and mapping UDF file type values to DragonFly vnode types.
- Implements NFS-style file handle conversion through a local `ifid` carrying inode number.
- Implements `udf_find_partmaps`, supporting ordinary type 1 maps and type 2 sparable partition maps, reading the first sparing table and recording valid sparing-table entries.

Dependencies:
- Uses DragonFly VFS, vnode, namecache, buffer cache, capability, mount-export, and module APIs.
- Uses UDF on-disk descriptors from `ecma167-udf.h`, OSTA helpers, and internal UDF structures from `udf.h`.
- Depends on `udf_vnode_vops` from `udf_vnops.c`.

Notable risks:
- Mount probing is intentionally narrow: it uses 2048-byte sectors, checks only anchor sector 256, and comments note missing checks for sector `n`, `n - 256`, and 512.
- The implementation supports one partition and limited partition-map types; unsupported maps fail mount.
- `udf_vget` allocates `size = UDF_FENTRY_SIZE + l_ea + l_ad` from on-disk fields after only tag validation, so malformed descriptors can stress allocation or bounds assumptions.
- The sparing table tag validation calls `udf_checktag(..., 0)`, which accepts only tag id 0 even though the table has a descriptor tag; this is a compatibility-sensitive area.
- Error paths close/free most state, but media parsing assumes many descriptor fields are trustworthy after tag checks.
