# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ialloc.h

Public/internal interface for interpreter allocation. It maps current interpreter context memory to shorthand macros:
- `gs_imemory`, `iimemory`, `imemory`
- local/global/system allocator aliases
- byte, struct, array, string allocation/free wrappers
- ref-array and string-ref wrappers when `ref` types are visible

Declares allocator initialization, GC request reset, validation, VM space selection, new mask, save level, and `make_i*struct` helpers that tag refs with the current VM space.
