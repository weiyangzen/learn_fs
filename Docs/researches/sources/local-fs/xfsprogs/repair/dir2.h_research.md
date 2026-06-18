# File Research: sources/local-fs/xfsprogs/repair/dir2.h

## Role

`dir2.h` declares the directory v2 repair interface.

## Exposed API

- `process_dir2`: validates and locally repairs a directory inode’s contents.
- `process_sf_dir2_fixi8`: rewrites shortform directory entries when `i8count` drops to zero.
- `dir2_is_badino`: tests whether a directory is known to have corrupt leaf/node linkage.

## Interactions

This header connects `dinode.c` to directory semantic checking and lets other code query the bad-directory cache.
