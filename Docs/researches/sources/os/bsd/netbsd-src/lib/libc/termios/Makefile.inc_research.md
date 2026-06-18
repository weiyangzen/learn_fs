# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/Makefile.inc

## Purpose
Adds termios libc source files and manual-page links.

## Key Elements
Adds speed accessors, raw-mode helper, terminal drain/flow/flush/get/set routines, process group/session helpers, and window-size helpers to `SRCS`.

## Dependencies
Uses `.PATH` for `${.CURDIR}/termios` and installs/manlinks `tcsetattr`, `tcsendbreak`, `tcgetpgrp`, `tcgetsid`, and window-size documentation.

## Behavior/Risks
Build-only file; coverage depends on every listed source being present and man links matching exported APIs.
