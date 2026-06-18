# File Research: sources/virtualization/nbdkit/filters/ext2/Makefile.am

Purpose: conditionally builds the ext2 filesystem filter and optional manual page.

Key details:
- Guarded by `HAVE_EXT2`.
- Builds `nbdkit-ext2-filter.la` from `ext2.c`, `io.c`, and `io.h`.
- Includes nbdkit headers, common includes, and utility headers.
- CFLAGS include `EXT2FS_CFLAGS` and `COM_ERR_CFLAGS`.
- Links common utils, Windows import support, `EXT2FS_LIBS`, and `COM_ERR_LIBS`.
- Applies shared filter linker script when configured.
- Generates `nbdkit-ext2-filter.1` from POD when available.

Integration notes:
- This work item includes only the build file; the actual ext2 filter implementation lives in adjacent `ext2.c`, `io.c`, and `io.h` outside this grouped file list.
