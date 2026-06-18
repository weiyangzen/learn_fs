# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmdebug.h

Allocator-debugging header. Declares fill-pattern bytes for allocated, local block, collected, deleted, and freed memory states. Aliases allocator debug enablement to `gs_debug['@']`.

Defines `gs_alloc_fill`, which conditionally calls `gs_alloc_memset` under `DEBUG`; in non-debug builds it compiles to no-op. This is used by allocator implementations to make memory misuse easier to diagnose.
