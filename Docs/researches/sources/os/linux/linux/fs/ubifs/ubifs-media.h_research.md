# File Research: sources/os/linux/linux/fs/ubifs/ubifs-media.h

## Purpose
Defines the UBIFS on-flash ABI: media format versioning, node constants, key/node type enums, logical eraseblock layout constants, and all packed node structures written to flash.

## Main Contents
- Format constants: `UBIFS_NODE_MAGIC`, `UBIFS_FORMAT_VERSION`, `UBIFS_RO_COMPAT_VERSION`, minimum LEB/journal/LPT/orphan/main-area sizes.
- Key model: simple key format, key types for inode/data/dentry/xentry nodes, fixed key offsets and key length limits.
- On-flash flags: inode flags, superblock flags, master-node flags, compression types, node group types.
- Packed node structs:
  - `struct ubifs_ch`: common node header with magic, CRC, sequence number, length, node type.
  - `struct ubifs_ino_node`: inode metadata, xattr accounting, compression type, attached inode data.
  - `struct ubifs_dent_node`: directory/xattr entry node with target inode, type, name, and cookie.
  - `struct ubifs_data_node`: file data payload with uncompressed size and compression metadata.
  - `struct ubifs_sb_node`: superblock, geometry, journal/LPT/orphan sizing, UUID, reserve pool, auth fields.
  - `struct ubifs_mst_node`: commit/master state, root index location, LPT roots, space accounting, auth hashes/HMAC.
  - `struct ubifs_ref_node`, `ubifs_idx_node`, `ubifs_cs_node`, `ubifs_orph_node`, auth/signature nodes.

## Important Design Points
- This file is a compatibility boundary. Layout, padding, endian annotations, and packed structs must remain stable unless the UBIFS format version and compatibility logic are updated.
- Node placement and node headers are generally 8-byte aligned; exceptions are explicitly called out for index and padding nodes.
- Xattr nodes reuse dentry node layout via `UBIFS_XENT_NODE_SZ`.
- Authentication support is baked into media structures through hash/HMAC fields in superblock, master node, branches, auth nodes, and signature nodes.
- Encryption context xattr name is intentionally short: `UBIFS_XATTR_NAME_ENCRYPTION_CONTEXT "c"`.

## Cross-File Relationships
- Included by `ubifs.h`, which builds in-memory structures and APIs around these media definitions.
- Used by `xattr.c` for xentry sizing, xattr inode data size limits, and encryption-context flag handling.
- Node constants and sizes are consumed by journal, TNC, replay, recovery, authentication, and I/O code across UBIFS.

## Risks / Review Notes
- Padding comments warn that changes require updates to zeroing helpers such as `zero_ino_node_unused()`, `zero_dent_node_unused()`, and `zero_trun_node_unused()` elsewhere.
- `UBIFS_FL_MASK` excludes newer flags like `UBIFS_XATTR_FL` and `UBIFS_CRYPT_FL` from the mask name’s apparent scope; users must understand it is the ioctl-style visible flag mask, not all UBIFS inode flags.
- Any modification to packed structs risks mount incompatibility and must be treated as on-disk format work.
