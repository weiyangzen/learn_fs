# File Research: sources/os/bsd/netbsd-src/sys/sys/trace.h

Read completely: 114 lines.

Defines legacy kernel trace event IDs and vtrace controls.

Key elements:
- File-system buffer trace points cover buffer cache hits/misses, writes, read-ahead, exec FOD, release, and realloc.
- Memory and paging trace points cover allocation, page-in waits, reclaim, fill-on-demand, swap-in, and swap I/O.
- Defines trace flag count, trace buffer size, and `vtrace()` operation constants.
- Kernel `TRACE` section declares trace globals, `pack()` for filesystem id/block packing, and `trace()` macro dispatch.
- Without `TRACE`, `trace(a,b,c)` compiles to nothing.

Risks and notes:
- Legacy diagnostic path; compiled behavior depends entirely on `TRACE`.
- Trace event IDs are observable by trace tooling.
