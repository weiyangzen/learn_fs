# File Research: sources/os/bsd/dragonflybsd/sys/vfs/udf/udf.h

Internal UDF filesystem state and helper interface header.

Key responsibilities:
- Defines `struct udf_node`, the per-vnode in-memory object containing vnode/device references, mount pointer, hash id, directory lookup offset, and copied UDF file entry.
- Defines `struct udf_mnt`, the per-mount state containing device and mount references, export state, logical block geometry, partition start/length, root ICB, vnode cache hash table, sparing-table metadata, and hash synchronization token.
- Defines `struct udf_dirstream`, the state machine used by `udf_vnops.c` to iterate file identifier descriptors across directory extents and fragmented FIDs.
- Defines conversion macros `VFSTOUDFFS` and `VTON`.
- Defines block-read helpers: `RDSECTOR`, `udf_readlblks`, and `udf_readalblks`. Logical block reads are rounded to the mount block mask; allocation-block reads include partition offset and one-block read-ahead.
- Defines `udf_getid`, mapping a long allocation descriptor to an inode-like file number by `lb_num`.
- Declares vnode allocation, vnode hash, descriptor tag validation, and `udf_vget` helpers.

Dependencies:
- Requires UDF on-disk structures from `ecma167-udf.h` and DragonFly kernel VFS/buffer/mount/list/token types.
- Uses DragonFly buffer APIs `bread` and `breadn`.

Notable risks:
- `udf_getid` assumes long allocation descriptors and uses only logical block number; multi-partition or descriptor variants could collide or be unsupported.
- Read helpers depend on `udfmp->bshift` and `bmask` being initialized from the logical volume descriptor.
- The mount structure has single-partition assumptions despite UDF descriptors supporting richer layouts.
