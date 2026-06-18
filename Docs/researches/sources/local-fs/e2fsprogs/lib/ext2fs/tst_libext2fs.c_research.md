# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_libext2fs.c

Adds libext2fs-specific commands into the debugfs command environment for testing. It sets `debug_prog_name` to `tst_libext2fs` and hooks `extra_cmds` to `libext2fs_cmds`.

The implemented command here is `do_block_iterate`, which resolves a file argument to an inode, parses optional flags, forces `BLOCK_FLAG_READ_ONLY`, and calls `ext2fs_block_iterate3`. The callback prints logical block count, physical block number, reference offset, and reference block.
