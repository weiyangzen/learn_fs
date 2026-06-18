# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_inode.c

Endian-safe inode field accessor implementation. It centralizes getting and setting inode mode, ownership, size, checksums, timestamps, link counts, block counts, flags, file ACL pointers, direct/indirect block slots, special-device payloads, and extent root access.

Key behavior:
- Handles Hurd high mode bits when `creator_os` is Hurd.
- Exposes low-level timestamp, UID/GID, link count, generation, extra inode size, and checksum fields.
- `ext4_inode_get_size` returns the high size word only for regular files on dynamic-revision filesystems.
- `ext4_inode_get_blocks_count` and `ext4_inode_set_blocks_count` implement normal, 48-bit, and huge-file block count encoding.
- Supports direct and indirect block pointer access through the inode `blocks[]` array.
- Encodes device numbers into inode direct block slots.
- Provides type and flag predicates and `ext4_inode_can_truncate`.
- Returns the inline extent root header by casting `inode->blocks`.

Notable dependencies:
- Uses superblock feature checks from `ext4_super.h`.
- Public declarations are in `include/ext4_inode.h`.
- Extent users rely on `ext4_inode_get_extent_header`.

Research notes:
- `uid` and `gid` accessors only use the low 16-bit disk fields despite returning `u32int`; Linux high UID/GID fields are not combined here.
- `ext4_inode_set_file_acl` stores the high ACL bits into a 16-bit field only when creator OS is Linux.
- Huge-file encoding depends on filesystem block size and `EXT4_INODE_FLAG_HUGE_FILE`.
