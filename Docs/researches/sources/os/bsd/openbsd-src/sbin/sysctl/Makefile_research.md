# File Research: sources/os/bsd/openbsd-src/sbin/sysctl/Makefile

Builds and installs `sysctl`.

Key settings:
- `PROG=sysctl`
- `MAN=sysctl.8`
- `afterinstall` creates `/usr/sbin/sysctl` symlink to `../../sbin/sysctl` and fixes ownership.

Role:
- Makes `sysctl` available in both `/sbin` and `/usr/sbin`.
