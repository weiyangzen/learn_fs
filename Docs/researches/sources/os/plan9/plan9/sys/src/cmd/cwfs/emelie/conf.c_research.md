# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/emelie/conf.c

Emelie deployment-specific cwfs configuration.

Key responsibilities:
- Defines `fs_mktime`.
- Sets `startsb` for `main` and `old` to `SUPER_ADDR`.
- `localconfinit()` sets:
  - `conf.nfile = 40000`
  - `conf.nodump = 1`, indicating jukebox is read-only
  - `conf.recovsb = 0`
  - `conf.nlgmsg = 100`
  - `conf.nsmmsg = 500`
- Exposes both `serve9p1` and `serve9p2`.

Research notes:
- A commented `conf.firstsb = 13219302` suggests shared lineage with the generic old-cw config but disabled here.
