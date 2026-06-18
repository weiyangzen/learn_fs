# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/fs64/conf.c

Runtime defaults for the `fs64` 8K/64-bit build.

Important behavior:
- `main` starts at superblock 2.
- `localconfinit()` enables dump reread verification and packet-sized message pools.
- Protocol table exposes `serve9p2`; comment notes 64-bit builds cannot serve 9P1 correctly due to name length.
