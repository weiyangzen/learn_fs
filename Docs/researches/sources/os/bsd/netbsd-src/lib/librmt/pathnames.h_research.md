# File Research: sources/os/bsd/netbsd-src/lib/librmt/pathnames.h

Read completely: 30 lines.

Defines the hardcoded helper paths used by `librmt`: `_PATH_RSH` is `/usr/bin/rsh` and `_PATH_RMT` is `/etc/rmt`. `rmtlib.c` can override the remote-shell command through `RCMD_CMD`, but the remote tape command path comes from this header.
