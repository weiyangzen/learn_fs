# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/common/tempnam.c

`tempnam.c` provides a local `tempnam()` implementation for V9/BSD/Plan 9 builds. It checks directory access, builds names from directory, prefix, pid, and sequence number, and loops while a generated path already exists.
