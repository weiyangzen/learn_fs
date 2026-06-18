# File Research: sources/os/bsd/netbsd-src/lib/libcurses/leaveok.c

Implements cursor-leave policy: `leaveok` and `is_leaveok`.

The file only toggles and reports the `__LEAVEOK` flag. `refresh.c` consumes this flag to decide whether `doupdate` should leave the physical cursor where output ended or move it to the logical window cursor.
