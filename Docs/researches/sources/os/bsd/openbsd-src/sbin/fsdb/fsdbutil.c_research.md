# File Research: sources/os/bsd/openbsd-src/sbin/fsdb/fsdbutil.c

## Scope

Utility functions for `fsdb`: command tokenization, command arity diagnostics, inode stat printing, and active-inode checks.

## Main APIs

- `crack(line, argc)` tokenizes a command line into up to eight whitespace-separated arguments.
- `argcount(cmdp, argc, argv)` prints command usage diagnostics.
- `printstat(label, inum, dp)` formats inode type, mode, size, timestamps, owner/group, link count, flags, block count, and generation.
- `checkactive()`, `checkactivedir()`, and `printactive()` validate and display the current inode.

## Control Flow

`printstat()` switches on inode type and special-cases inline symlink contents when size is below `fs_maxsymlinklen` and `di_blocks` is zero. It formats timestamps with `ctime()` when possible and falls back to numeric seconds. Owner and group names are resolved through `user_from_uid()` and `group_from_gid()`.

## Dependencies

- Uses `DIP()` macros and global `sblock` from fsck_ffs.
- Uses `curinode`/`curinum` from `fsdb.c`.
- Uses system user/group lookup helpers.

## Risks And Edge Cases

- `crack()` uses a static fixed-size argv array of eight entries; longer commands are silently truncated by token count.
- `printactive()` handles unknown inode modes without mutating state.
