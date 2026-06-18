# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_bitmaps.c

Interactive/scriptable test shell for libext2fs bitmap operations. It uses the `ss` command subsystem and exposes commands for setting up an in-memory test filesystem, dumping block/inode bitmaps, setting/clearing/testing single bits and ranges, finding first zero/set blocks or inodes, and clearing entire bitmaps.

`setup_filesystem` initializes a synthetic filesystem through `ext2fs_initialize` and `test_io_manager`, sets the requested bitmap backend type, and allocates fresh block and inode bitmaps. The default mode uses 64-bit bitmaps.

The program can run interactively, execute one request via `-R`, or source a command file via `-f`. It carefully resets `getopt` state for command handlers so repeated shell commands parse correctly across different libc implementations.
