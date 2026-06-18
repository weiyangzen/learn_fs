# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs64/conf.c

64-bit cwfs configuration.

Key responsibilities:
- Defines `fs_mktime`.
- Sets `startsb` for `main` to block `2`.
- `localconfinit()` sets:
  - dumps enabled
  - `conf.dumpreread = 1`
  - `conf.firstsb = 0`
  - `conf.recovsb = 0`
  - `conf.nlgmsg = 1100`
  - `conf.nsmmsg = 500`
- `fsprotocol[]` exposes only `serve9p2`.

Research notes:
- The file explicitly comments that 64-bit file servers cannot correctly serve 9P1 because `NAMELEN` is too large.
