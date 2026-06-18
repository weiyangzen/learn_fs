# File Research: sources/local-fs/e2fsprogs/e2fsck/iscan.c

## Purpose
Standalone performance test for scanning an ext inode table.

## Main Behavior
- CLI: `iscan [-F] [-I inode_buffer_blocks] device`.
- Optional `-F` flushes the device via `ext2fs_sync_device()`.
- Opens filesystem with `ext2fs_open()`.
- Starts an inode scan with configurable inode buffer blocks.
- Iterates all inodes with `ext2fs_get_next_inode()`.
- Prints memory/time/I/O resource stats and total inode count.

## Resource Tracking
Contains local `resource_track` implementation similar to e2fsck timing support:
- records wall/user/system time,
- tracks heap growth or malloc info,
- tracks I/O stats from the channel manager.

## Integration
Built as optional `iscan` and `iscan.static` helper targets. It links against the same ext2fs/support libraries.

## Risks / Notes
The getopt string is `"FI"` but `-I` consumes `optarg`; normally this should be `"FI:"`. As read, argument parsing for `-I` appears suspect.
