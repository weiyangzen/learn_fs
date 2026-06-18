# File Research: sources/os/linux/linux-stable/fs/befs/befs_fs_types.h

This header defines BeFS on-disk and host-side filesystem structures. It is the schema layer for superblocks, inodes, datastreams, block runs, small attributes, and B+tree nodes.

Key constants:
- `BEFS_NAME_LEN` is 255.
- `BEFS_SYMLINK_LEN` is 144 for inline symlink storage.
- `BEFS_NUM_DIRECT_BLOCKS` is 12.
- `BEFS_DBLINDIR_BRUN_LEN` is 4, used by double-indirect datastream mapping.
- Superblock magic values: `BEFS_SUPER_MAGIC1`, `BEFS_SUPER_MAGIC2`, `BEFS_SUPER_MAGIC3`.
- Inode magic and flags include `BEFS_INODE_IN_USE`, `BEFS_LONG_SYMLINK`, and transaction/logging flags.
- `BEFS_BTREE_MAGIC` and `enum btree_types` define BeFS B+tree metadata.

Important types:
- `fs64`, `fs32`, and `fs16` are bitwise-tagged on-disk endian-sensitive integer types.
- `befs_disk_block_run` is the packed on-disk allocation-group/start/len tuple.
- `befs_block_run` is the host-side equivalent.
- `befs_super_block` is the packed on-disk superblock.
- `befs_disk_data_stream` and `befs_data_stream` describe direct, indirect, and double-indirect file mappings.
- `befs_inode` is the packed on-disk inode, containing metadata plus either datastream or inline symlink bytes.
- `befs_disk_btree_super`, `befs_btree_super`, `befs_btree_nodehead`, and `befs_host_btree_nodehead` define B+tree superblock/node headers.

Integration:
- `endian.h` converts these disk structures into host structures.
- `super.c` consumes `befs_super_block`.
- `inode.c` and `linuxvfs.c` consume `befs_inode`.
- `datastream.c` consumes datastream and block-run types.
- `btree.c` consumes B+tree types.

Risk notes:
- The file intentionally uses packed structures and bitwise endian types; incorrect direct access without conversion would create cross-endian bugs.
- The double-indirect constant has an inline comment questioning whether it means four filesystem blocks or 4 KiB, which is relevant for large block-size compatibility.
