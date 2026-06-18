# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/all.h

Common include and global declaration header for cwfs.

Important elements:
- Pulls in Plan 9 libc, fcall, disk, bio, and IP headers plus generated `dat.h` and `portfns.h`.
- Defines common macros like `CHAT()` and qid helpers.
- Declares global filesystem state: uid/gid tables, locks, time, channels, queues, files, wpaths, flags, devices, superblock starts, and config fields.
- Declares configuration globals such as `service`, `filsys`, `fspar`, read-only/auth/noatime switches, and buffer/file accounting.
