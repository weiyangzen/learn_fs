# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/strmdep.h

`strmdep.h` is the STREAMS machine-dependent shim. In this illumos version it is small: `strbcpy()` maps to `bcopy()`, `saveaddr()` is an empty macro retained for historical allocator tracking hooks, and `str_aligned()` checks whether a pointer is aligned to `sizeof (long)`.

The file exists so STREAMS code can refer to machine-dependent operations through stable macros even when the current platform implementation does not need special handling.
