# File Research: sources/os/bsd/openbsd-src/sbin/restore/Makefile

## Purpose

Builds `restore` and installs `rrestore` as a hard link.

## Build Definition

The program is `restore`, linked also as `rrestore`. It defines `RRESTORE`, compiles restore sources plus `dumprmt.c` from `../dump`, installs `restore.8`, and uses `.PATH` to find dump-shared code.
