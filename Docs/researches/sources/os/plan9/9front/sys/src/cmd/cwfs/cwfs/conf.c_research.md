# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/cwfs/conf.c

Generic old-cw runtime defaults.

Important behavior:
- `main` starts at superblock 2.
- `localconfinit()` sets `conf.nfile=40000`, enables dumps by default, and sizes message pools.
- Contains a commented read-only jukebox `nodump` setting.
- Protocol table exposes `serve9p2`.
