# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/mcolor/mcolor.mk

Makefile for installing troff color macro support.

Key responsibilities:
- Copies `color.sr` to `tmac.color`.
- Installs `tmac.color` into `TMACDIR`.
- Provides clean, clobber, and `changes` targets.

Important behavior:
- `changes` rewrites makefile defaults and updates path strings in `mcolor.5`.
