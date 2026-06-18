# File Research: sources/teaching/os161/kern/include/kern/resource.h

Defines resource usage and limit ABI structures.

Key contents:
- Priority constants and selectors.
- `struct rusage` with time, memory, I/O, signal, and context-switch counters.
- RLIMIT constants including `RLIMIT_FSIZE`.
- `struct rlimit` and `RLIM_INFINITY`.

Relevance:
- `RLIMIT_FSIZE` is semantically related to file-size growth, though the listed SFS code enforces only filesystem layout size limits.
