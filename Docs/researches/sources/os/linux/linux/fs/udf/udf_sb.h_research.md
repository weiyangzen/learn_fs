# File Research: sources/os/linux/linux/fs/udf/udf_sb.h

Purpose: UDF per-superblock state, flags, and partition map structures.

Key contents:
- Defines max supported UDF revisions for read/write.
- Defines mount/runtime flags for extended FE, streams, short AD, AD-in-ICB, strict mode, undelete/unhide, uid/gid handling, session/lastblock/blocksize, inconsistent state, and RW incompatibility.
- Defines partition flags and partition map type constants.
- `struct udf_meta_data`, `struct udf_sparing_data`, and `struct udf_virtual_data` hold type-specific partition data.
- `struct udf_bitmap` holds unallocated bitmap buffers.
- `struct udf_part_map` describes logical partition root/length/type, free-space source, type-specific data, translation function, volume sequence number, and flags.
- `struct udf_sb_info` stores partition maps, volume ID, session/anchor/last block, LVID buffer, permissions, credential lock, record time, serial number, UDF revision, flags, NLS map, VAT inode, and allocation mutex.
- Includes flag helpers and `UDF_SB()`.

Integration:
- Included by `udfdecl.h` and directly by most implementation files.
- `super.c` initializes and frees most members; `partition.c` consumes partition maps; allocation and name code updates LVID and flags.

Risks and invariants:
- `s_alloc_mutex` protects LVID dirty state and allocation-related shared state.
- Partition map function pointer determines logical-to-physical semantics.
- `UDF_FLAG_RW_INCOMPAT` is a central mount policy signal for unsupported write cases.
