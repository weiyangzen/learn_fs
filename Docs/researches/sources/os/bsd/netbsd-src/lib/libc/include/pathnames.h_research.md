# File Research: sources/os/bsd/netbsd-src/lib/libc/include/pathnames.h

Private libc pathname header currently defining `_PATH_BIN_RCMD`.

Behavior:
- If `RESCUEDIR` is defined, `_PATH_BIN_RCMD` is `RESCUEDIR "/rcmd"`.
- Otherwise `_PATH_BIN_RCMD` is `"/bin/rcmd"`.

Used for libc code that needs the rcmd helper path.
