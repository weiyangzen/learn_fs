# File Research: sources/os/plan9/9front/sys/src/cmd/replica/revdump.c

Utility that dumps reverse-proto traversal results. For each enumerated file it prints new path, mode flags, uid, gid, and old path.

Despite the usage string saying `protodump`, the file calls `revrdproto()` and accepts `-r root`.
