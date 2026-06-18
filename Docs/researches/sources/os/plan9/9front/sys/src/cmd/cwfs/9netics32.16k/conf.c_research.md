# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/9netics32.16k/conf.c

Build-specific runtime defaults for a 9netics 32-bit, 16K-block cwfs instance.

Important behavior:
- Sets `fs_mktime` from `DATE`.
- Declares a `main` start superblock at block 2.
- `localconfinit()` disables dump-read-reread, sets no first/recovery superblock override, and sizes large/small message pools.
- Protocol table exposes only `serve9p2`.
