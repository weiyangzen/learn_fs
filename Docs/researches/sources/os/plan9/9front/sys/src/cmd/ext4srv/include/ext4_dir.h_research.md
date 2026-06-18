# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_dir.h

Directory entry accessor and directory manipulation API header.

Key behavior:
- Defines `ext4_dir_iter` for internal linear directory traversal and `ext4_dir_search_result` for found entries with their containing block.
- Provides inline accessors for directory entry inode, record length, name length, and inode type, including old revision name-length behavior.
- Declares directory block checksum verification/update and tail initialization helpers.
- Declares iterator init/next/fini, directory entry writing, entry add/find/remove, in-block insertion/search, and search-result destruction.

Notable dependencies:
- Includes `ext4_types.h`, `ext4_misc.h`, `ext4_blockdev.h`, and `ext4_super.h`.
- Implemented by `ext4_dir.c` and used by htree directory code and public directory operations.

Research notes:
- The inline inode type accessor returns `EXT4_DE_UNKNOWN` for older on-disk formats without file type storage.
- Checksum-tail support is exposed here but actual checksum decisions are in the implementation.
