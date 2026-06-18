# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/9netics32.16k/conf.c

Configuration module for a 9netics 32-bit, 16 KiB-block cwfs build.

It defines build time `fs_mktime`, starts the default filesystem at superblock `"main", 2`, initializes local configuration values for dump behavior, superblock selection, and message-buffer counts, and enables both `serve9p1` and `serve9p2`.

This profile can serve legacy 9P1 because it uses the 32-bit layout.
