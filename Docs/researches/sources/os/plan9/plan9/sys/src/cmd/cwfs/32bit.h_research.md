# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/32bit.h

cwfs 32-bit on-disk layout constants.

It fixes `NAMELEN` to 28, `NDBLOCK` to 6, `NIBLOCK` to 2, and defines `Off` as `long`. The comments warn not to change these values because they preserve compatibility with old 32-bit Plan 9 file-server disks and 9P1 service.

It defines `COMPAT32` and maps `swaboff` to `swab4`.
