# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/emelie/conf.c

Site-specific runtime defaults for the `emelie` cwfs build.

Important behavior:
- Defines `main` and `old` start superblocks at `SUPER_ADDR`.
- `localconfinit()` sets `conf.nfile=40000` and `conf.nodump=1` because the jukebox is read-only.
- Message pool defaults match old cw builds.
- Protocol table exposes `serve9p2`.
