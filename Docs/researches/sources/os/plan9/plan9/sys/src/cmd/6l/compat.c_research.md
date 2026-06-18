# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/compat.c

This file supplies simple allocation and compatibility helpers for the amd64 linker. It implements a hunk-based `malloc`, `calloc`, no-op `free`, and unsupported `realloc`. Allocation rounds to 8-byte alignment and pulls memory from linker hunks via `gethunk`.

`mysbrk` delegates to `sbrk`, and `setmalloctag` is a no-op compatibility stub. `fileexists` checks whether `stat` succeeds, deliberately treating an oversized stat result as still proving file existence.

Filesystem relevance is practical: `fileexists` is used by library path resolution, and the allocation wrappers support the linker’s object/archive ingestion without relying on a conventional allocator.
