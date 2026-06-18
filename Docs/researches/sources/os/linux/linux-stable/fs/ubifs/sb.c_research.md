# File Research: sources/os/linux/linux-stable/fs/ubifs/sb.c

## Purpose
Implements UBIFS superblock handling: empty-volume default formatting, superblock reading/writing, validation, authentication checks, resize bookkeeping, free-space fixup, and enabling encryption.

## Key Behavior
- `create_default_filesystem()` builds a minimal UBIFS image on an empty UBI volume: superblock, two master nodes, root index node, root inode, LPT metadata, and initial commit-start log node.
- Default geometry is derived from volume size, LEB size, minimum journal/log/orphan/LPT constraints, and reserved-pool defaults.
- `ubifs_read_superblock()` reads the on-flash superblock, fills `struct ubifs_info`, enforces format compatibility, handles automatic LEB-count growth, and derives area boundaries.
- `validate_sb()` rejects inconsistent geometry, unsupported key formats, invalid journal/fanout/LEB counts, bad compression IDs, invalid time granularity, and incompatible encryption/double-hash combinations.
- `authenticate_sb_node()` supports authenticated mounts through either superblock HMAC or an offline signature node following the superblock.
- `ubifs_fixup_free_space()` performs first-mount NAND free-space rewrite/unmap when `UBIFS_FLG_SPACE_FIXUP` is set, then clears the flag for future mounts.
- `ubifs_enable_encryption()` sets `UBIFS_FLG_ENCRYPTION` after checking crypto support, R/W state, and format version.

## Important Dependencies
- Uses UBI LEB operations through UBIFS wrappers: `ubifs_leb_change()`, `ubifs_leb_unmap()`, `ubifs_leb_read()`.
- Calls LPT creation/lookup paths: `ubifs_create_dflt_lpt()`, `ubifs_get_lprops()`, `ubifs_lpt_lookup()`.
- Depends on authentication helpers such as `ubifs_hmac_wkm()`, `ubifs_node_verify_hmac()`, and `ubifs_sb_verify_signature()`.
- Exposes state consumed by mount, budgeting, LPT, journal, and TNC initialization.

## Invariants and Risks
- The superblock is normally immutable during UBIFS operation; only controlled updates such as resize, free-space-fixup clearing, authentication HMAC conversion, and encryption enablement rewrite it.
- Format-version checks are central: newer writable formats are rejected unless read-only compatibility permits R/O mounting.
- Geometry validation protects downstream code from impossible LEB layouts and malformed index/node size assumptions.
