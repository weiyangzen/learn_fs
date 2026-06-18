# File Research: sources/os/bsd/openbsd-src/sbin/dump/main.c

## Purpose
Main driver for UFS `dump`.

## Key Behavior
- Parses dump level and options for block size, density, tape/file target, estimated-only mode, dumpdates update, nodump honor level, tape geometry, remote output, and historical option syntax.
- Supports dumping a full mounted filesystem, a device/fstab entry, or a list of files/directories from one filesystem.
- Resolves device paths through `opendev()`, fstab lookup, raw device conversion, and DUID handling.
- Initializes `spcl` tape header metadata: host, device, filesystem name, dump level, date, and previous dump date.
- Opens the raw disk, reads disklabel info, probes UFS superblock candidates from `SBLOCKSEARCH`, and validates UFS1/UFS2.
- Allocates inode maps sized to the filesystem inode count.
- Computes dump size estimates, including map overhead, trailer blocks, tape changes, cartridge/9-track density assumptions, and blocks-per-file rounding.
- Runs the four dump passes:
  - Pass I maps regular files and directories.
  - Pass II propagates needed directory inclusion.
  - Pass III dumps directories.
  - Pass IV dumps regular files and non-directory inodes.
- Writes end headers, prints stats, updates dumpdates, rewinds/closes media, and broadcasts completion.
- `obsolete()` converts old compact dump option syntax into modern getopt-compatible arguments.

## Notes
`main.c` orchestrates the whole dump lifecycle but delegates inode walking to `traverse.c`, tape concurrency to `tape.c`, dumpdates to `itime.c`, and operator UI to `optr.c`.
