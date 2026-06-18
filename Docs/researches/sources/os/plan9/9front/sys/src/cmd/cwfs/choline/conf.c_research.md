# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/choline/conf.c

Site-specific runtime defaults for the `choline` cwfs build.

Important behavior:
- `main` starts at superblock 2.
- `localconfinit()` sets `conf.nfile=60000`, enables dumps, uses `firstsb=12565379`, and sizes message pools.
- Protocol table exposes `serve9p2`.
