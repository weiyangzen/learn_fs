# File Research: sources/local-fs/xfsprogs/repair/versions.c

Parses and updates filesystem feature/version state from the superblock.

Global feature state:
- Attribute support, attr2, inode nlink, quotas, aligned inodes, superblock feature bits, extent flag bit.
- `fs_ino_alignment` stores inode chunk alignment in filesystem blocks.

Core functions:
- `parse_sb_version` validates supported version/features, rejects shared-version bit, detects unknown v5 features, initializes feature globals, registers quota inode numbers, and records inode alignment.
- `update_sb_version` updates the in-core superblock from feature globals, forces v2 inode nlink bit, adds attr/attr2/quota bits when needed, clears bogus quota flags, clears quota/alignment bits when unsupported, and refreshes mount feature flags.

Important behavior:
- V1 inode filesystems are warned as being converted to v2 inode behavior.
- Unsupported unknown compat/rocompat/incompat features cause repair to exit.
- Quota flags are sanitized even in no-modify mode because the in-core superblock will not be flushed.
