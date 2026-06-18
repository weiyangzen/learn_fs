# File Research: sources/virtualization/nbdkit/filters/pause/Makefile.am

This build file compiles `nbdkit-pause-filter.la` from `pause.c` only on non-Windows platforms because the implementation relies on Unix domain sockets. It includes core headers and `common/utils`, links `libutils.la`, and optionally builds the POD-derived manual.

The conditional `if !IS_WINDOWS` is the key build gate. The filter's runtime dependency on Unix socket path limits and POSIX socket APIs is reflected directly in the build rules.
