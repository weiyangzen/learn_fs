# File Research: sources/os/bsd/freebsd-src/sbin/devfs/Makefile

## Purpose
Builds the `devfs` control utility and installs default config/rules files.

## Main Elements
- `CONFS=devfs.conf devfs.rules`
- Installs `devfs.rules` under `/etc/defaults` with mode `600`.
- `PROG=devfs`
- `SRCS=devfs.c rule.c`
- `MAN=devfs.8`
