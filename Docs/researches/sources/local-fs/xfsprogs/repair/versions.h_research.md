# File Research: sources/local-fs/xfsprogs/repair/versions.h

Header for repair feature/version globals and parsing/updating functions.

Exports:
- Feature globals such as `fs_attributes`, `fs_quotas`, `fs_aligned_inodes`, and `fs_has_extflgbit`.
- `fs_ino_alignment`.
- `update_sb_version` to modify superblock version/features from repair state.
- `parse_sb_version` to initialize repair globals from a mounted superblock.

Used by scanner and main repair setup to decide inode alignment checks and feature-specific repair behavior.
