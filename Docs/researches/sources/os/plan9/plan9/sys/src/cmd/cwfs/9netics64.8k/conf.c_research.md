# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics64.8k/conf.c

Configuration module for a 9netics 64-bit, 8 KiB-block cwfs build.

It defines `fs_mktime`, default superblock startup, and local message/dump settings like the 32-bit variant, but its protocol table enables only `serve9p2`. The comment states 64-bit file servers cannot serve 9P1 correctly because `NAMELEN` is too large.

This profile is for the incompatible 64-bit disk format.
