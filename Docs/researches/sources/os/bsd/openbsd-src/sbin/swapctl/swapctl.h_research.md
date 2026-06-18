# File Research: sources/os/bsd/openbsd-src/sbin/swapctl/swapctl.h

Small shared header for `swapctl`.

Contents:
- NetBSD/OpenBSD copyright/license.
- Declares `list_swap(int pri, int kflag, int pflag, int dolong)`.

Role:
- Connects command parser in `swapctl.c` to listing implementation in `swaplist.c`.
