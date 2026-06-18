# File Research: sources/os/bsd/freebsd-src/sbin/mount/vfslist.c

## Summary
Implements filesystem-type include/exclude filtering for `mount -t`.

## Main Elements
- `makevfslist()`: parses comma-separated filesystem names into a NULL-terminated array, with leading `no` meaning exclusion mode.
- `checkvfsname()`: returns whether a filesystem should be skipped based on the parsed list and global `skipvfs`.

## Research Notes
The parser mutates the input string in place by replacing commas with NUL terminators.
