# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/fs/conf.c

`fs` deployment-specific cwfs configuration using 4K blocks and 32-bit layout.

Key responsibilities:
- Defines `fs_mktime`.
- Sets `startsb` for `main` to `810988`, with comment noting a discontinuity before superblock `696262`.
- `localconfinit()` sets:
  - dumps enabled
  - `conf.dumpreread = 1`
  - `conf.firstsb = 0`
  - `conf.recovsb = 0`
  - `conf.nlgmsg = 1100`
  - `conf.nsmmsg = 500`
- Exposes both `serve9p1` and `serve9p2`.

Research notes:
- The larger large-message buffer count is annotated as for packets at 8576 bytes.
