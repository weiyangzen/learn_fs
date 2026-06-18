# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/fs/conf.c

Runtime defaults for the `fs` 4K/32-bit build.

Important behavior:
- `main` start superblock is set to `810988`, with a comment noting a discontinuity before block `696262`.
- `localconfinit()` enables dump reread verification and uses large message pools sized for packets.
- Protocol table exposes `serve9p2`.
