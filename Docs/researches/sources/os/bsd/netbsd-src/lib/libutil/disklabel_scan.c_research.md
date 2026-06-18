# File Research: sources/os/bsd/netbsd-src/lib/libutil/disklabel_scan.c

## Purpose
Scans a buffer for a valid NetBSD disklabel.

## Key Details
- Searches every 4 bytes for a `struct disklabel`.
- Requires both `d_magic` and `d_magic2` to equal `DISKMAGIC`.
- Rejects labels with too many partitions or nonzero `disklabel_dkcksum`.
- Returns `0` on success, `1` on failure.

## Dependencies and Role
- Storage-facing utility for locating labels in raw sector buffers.
