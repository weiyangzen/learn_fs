# File Research: sources/local-fs/e2fsprogs/e2fsck/scantest.c

This is a standalone inode-scan performance test program, not part of normal e2fsck pass logic.

Behavior:
- Opens a hardcoded device path `/dev/hda3` with `ext2fs_open()`.
- Opens an inode scan with `ext2fs_open_inode_scan()`.
- Iterates all inodes with `ext2fs_get_next_inode()`.
- Prints `i_blocks` for inodes whose `i_links_count` is nonzero.
- Closes the filesystem and prints resource usage.

Local resource tracking:
- Defines a small `struct resource_track` with wall/user/system start times and initial program break.
- `init_resource_track()` captures starting memory and rusage.
- `timeval_subtract()` computes elapsed seconds.
- `print_resource_track()` prints memory delta and elapsed/user/system time.

Integration points:
- Uses libext2fs directly, plus `com_err` for error reporting.
- Includes e2fsprogs version and ext2fs headers.
- Uses `_()` translation macro in printf/com_err messages.

Risk notes:
- The device path is hardcoded and obsolete; running it unmodified is environment-specific.
- It exits immediately on any libext2fs open/scan/read error.
- It is useful as a benchmark/dev utility rather than production fsck logic.
