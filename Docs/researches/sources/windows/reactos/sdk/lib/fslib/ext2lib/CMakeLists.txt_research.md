# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/CMakeLists.txt

Read completely: 21 lines.

This build file defines the `ext2lib` static/library target from ext2 formatting sources: bad-block handling, bitmaps, disk I/O, group/inode/memory/superblock/UUID helpers, the main `Mke2fs.c`, and `Mke2fs.h`. It adds `Mke2fs.h` as a precompiled header source and depends on `psdk`.

For MSVC builds it disables warning C4267 about possible loss converting `size_t` to `__u8`.

Security/reliability notes: no runtime behavior. Build behavior depends on `Mke2fs.h` being a stable PCH root for all listed sources.
