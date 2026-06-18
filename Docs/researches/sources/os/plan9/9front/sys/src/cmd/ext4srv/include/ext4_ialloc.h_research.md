# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_ialloc.h

Inode allocation API header.

Key behavior:
- Declares inode bitmap checksum setter.
- Declares inode freeing with directory/non-directory counter adjustment.
- Declares inode allocation and documents that it uses a simpler algorithm than Linux's Orlov allocator.

Notable dependencies:
- Includes `ext4_config.h` and `ext4_types.h`.
- Implemented by `ext4_ialloc.c`; called through higher-level filesystem allocation functions.

Research notes:
- The header refers to `struct ext4_fs` and `struct ext4_bgroup` through included type declarations rather than including the full filesystem header.
