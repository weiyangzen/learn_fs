# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/cwfs/conf.c

Generic old-cw build configuration.

Key responsibilities:
- Defines `fs_mktime` from `DATE`.
- Sets `startsb` for `main` to block `2`.
- `localconfinit()` sets cwfs-specific defaults:
  - `conf.nfile = 40000`
  - dumps enabled
  - `conf.firstsb = 13219302`
  - `conf.recovsb = 0`
  - `conf.nlgmsg = 100`
  - `conf.nsmmsg = 500`
- Exposes both `serve9p1` and `serve9p2` in `fsprotocol[]`.

Research notes:
- This variant is paired with `cwfs/dat.h`, which selects 16K blocks and 32-bit layout.
- `conf.firstsb` is preseeded to a specific superblock address, likely for an existing old-cw deployment.
