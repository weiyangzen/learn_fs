# File Research: sources/local-fs/ocfs2-tools/debugfs.ocfs2/include/dump.h

## Role

`dump.h` declares the formatting API used by `debugfs.ocfs2` command handlers and journal/path/block helpers.

## Data Types

It defines helper contexts for directory listing (`list_dir_opts`) and directory-block walking (`dirblocks_walk`).

## API Coverage

The header declares dump routines for superblocks, inodes, local allocators, truncate logs, extents, chains, groups, directory entries/blocks, directory indexes, JBD2 journal structures, slot maps, heartbeat blocks, inode paths, block mapping, icheck output, checksums, xattrs, fragmentation, and refcount blocks/records.

## Role In Architecture

It separates command logic from output formatting, letting `commands.c`, `journal.c`, `stat_sysdir.c`, and search helpers share the same presentation code.
