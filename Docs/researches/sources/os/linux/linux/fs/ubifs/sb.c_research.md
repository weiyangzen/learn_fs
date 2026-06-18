# File Research: sources/os/linux/linux/fs/ubifs/sb.c

Read completely: 956 lines.

This file implements UBIFS superblock handling, including default filesystem creation on an empty UBI volume, superblock parsing and validation, authentication checks, free-space fixup, and enabling encryption.

Main entry points: `ubifs_read_superblock`, `ubifs_write_sb_node`, `ubifs_fixup_free_space`, and `ubifs_enable_encryption`.

Key behavior: `create_default_filesystem` formats an empty volume by deriving default journal/log/LPT/orphan/main-area geometry, creating the superblock, master node, root index node, root inode, and initial commit-start node. It also initializes authentication fields when authenticated mounting is requested and records hashes for LPT and root index metadata.

Superblock read path: `ubifs_read_superblock` reads the on-flash superblock, handles read-only compatibility for future format versions, chooses the key hash and key format, copies geometry and mount defaults into `struct ubifs_info`, authenticates the node, rejects unknown feature flags, auto-resizes to the UBI volume size when allowed, derives area boundaries, and calls `validate_sb`.

Validation and feature checks: `validate_sb` verifies min I/O and LEB size against the real UBI device, checks minimum counts for log/LPT/orphan/main areas, validates journal and fanout limits, checks reserved-pool and time-granularity bounds, and enforces format-version requirements for double hashing and encryption.

Authentication: `authenticate_sb_node` enforces consistency between mount authentication options and on-flash authentication flags, verifies hash algorithm selection, supports either superblock HMAC or an offline image signature node, and validates the well-known-message HMAC against the supplied key.

Free-space fixup: `ubifs_fixup_free_space` rewrites or unmaps LEBs containing free space when `UBIFS_FLG_SPACE_FIXUP` is set, then clears the flag and marks the superblock for rewrite. This protects NAND parts where apparent `0xff` free space may have been programmed with non-erased ECC.

Encryption enablement: `ubifs_enable_encryption` requires fscrypt support, read-write media, and format version 5 or newer, then sets `UBIFS_FLG_ENCRYPTION` in the superblock and writes it immediately.

Important interactions: `super.c` calls this file during mount and remount; LPT creation and lprops lookup are used for default formatting and space fixup; authentication helpers are supplied by UBIFS auth code; low-level node I/O and HMAC writing come from `io.c`.

Reliability notes: the superblock is normally immutable after formatting except for controlled flag/count updates. This file is therefore the gatekeeper for on-flash compatibility and must reject inconsistent geometry before later mount code trusts derived LEB ranges.
