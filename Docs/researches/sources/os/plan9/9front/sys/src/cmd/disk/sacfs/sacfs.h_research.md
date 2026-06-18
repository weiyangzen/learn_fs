# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/sacfs.h

## Purpose
Defines the on-disk SAC filesystem metadata structures.

## Key Contents
- `Magic = 0x5acf5` identifies SAC images.
- `NAMELEN = 28` fixes stored name, uid, and gid field lengths.
- `SacDir` stores fixed-size name/uid/gid plus big-endian qid, mode, atime, mtime, length, and block-table offset fields.
- `SacHeader` stores magic, total image length, block size, and an MD5 field.

## Notes
Although `SacHeader.md5` exists in the format, the builder and server in this group do not compute or validate it.
