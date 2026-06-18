# File Research: sources/os/plan9/plan9/sys/src/cmd/9660srv/data.c

Purpose: global data definitions for 9660srv.

Key behavior: defines common error strings, default service name, default image file pointer, external ISO subsystem symbol, and `xsublist` containing `isosub`.

Integration notes: `main.c` iterates `xsublist` during reset and attach. Adding more filesystem formats would extend this table.
