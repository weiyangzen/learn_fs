# File Research: sources/os/linux/linux-stable/fs/ubifs/ubifs-media.h

## Summary
Defines the UBIFS on-flash format: magic/version constants, geometry limits, key/node type identifiers, flags, compression IDs, and all packed node structures stored on UBI media.

## Main Responsibilities
- Declares UBIFS format versioning and read-only compatibility values.
- Defines minimum logical eraseblock sizes, reserved LEB area layout, journal/head numbers, block size, key sizes, and LPT geometry constants.
- Defines inode types, key formats, key hash types, key types, node types, LPT node types, master node flags, node group flags, and superblock flags.
- Defines maximum node sizes and fixed-size hash/HMAC storage used by authenticated UBIFS.
- Describes every on-flash node with packed C structs: common header, inode, directory/xattr entry, data, truncation, padding, superblock, master, reference, authentication, signature, index, commit-start, and orphan nodes.

## Important Structures
- `struct ubifs_ch`: common node header containing magic, CRC, sequence number, length, type, and group type.
- `struct ubifs_ino_node`: inode metadata plus optional inline inode data or xattr value.
- `struct ubifs_dent_node`: directory entry and extended-attribute entry format.
- `struct ubifs_data_node`: keyed file data node with uncompressed size, compression type, and encryption-aware compressed size.
- `struct ubifs_sb_node`: filesystem geometry, flags, compressor, UUID, reserved-pool, authentication, and signature metadata.
- `struct ubifs_mst_node`: committed root/index/log/LPT/orphan/accounting state.
- `struct ubifs_branch` and `struct ubifs_idx_node`: on-flash index tree references.

## Research Notes
The file is the ABI between UBIFS implementations and existing media. Padding fields explicitly warn that zeroing helpers must be updated if layouts change. Node type values are intentionally low and contiguous because other code indexes arrays with them, and inode/data/dentry/xentry node values must match corresponding key type values.

## Risks
Any change here is an on-flash format change. Alignment, padding zeroing, endian annotations, and size constants are part of the compatibility contract. Authentication and encryption fields also alter node sizing expectations in index branches and data nodes.
