# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsync.c

Implements Ghostscript wrappers over platform synchronization primitives.

Key behavior:
- `gx_semaphore_alloc` computes the actual platform semaphore storage size, chooses movable or immovable Ghostscript allocation based on `gp_semaphore_open(0)`, initializes the native semaphore, and records the allocator.
- `gx_semaphore_free` closes the native semaphore and frees the wrapper.
- `gx_monitor_alloc` does the same for platform monitor objects using `gp_monitor_sizeof` and `gp_monitor_open`.
- `gx_monitor_free` closes and frees monitor objects.
- Re-declares the wait/signal and enter/leave macros locally to keep implementation and header signatures consistent.

Dependencies:
- Platform primitives from `gpsync.h` via `gxsync.h`.
- Ghostscript allocation APIs from `gsmemory.h`.
- Error/type support from `gx.h` and `gserrors.h`.

Research notes:
- The wrapper structs place the native platform object last because its true size is platform-dependent.
- Allocation failure and platform-open failure return `NULL`; successful wrappers remember the allocator needed for cleanup.
