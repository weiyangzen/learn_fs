# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxsync.h

Defines Ghostscript’s synchronization abstraction for semaphores and monitors.

Key declarations:
- `gx_semaphore_t` stores an allocator pointer plus platform `gp_semaphore` storage.
- `gx_semaphore_alloc` / `gx_semaphore_free`.
- `gx_semaphore_wait` and `gx_semaphore_signal` macros delegate to platform primitives.
- `gx_monitor_t` stores an allocator pointer plus platform `gp_monitor` storage.
- `gx_monitor_alloc` / `gx_monitor_free`.
- `gx_monitor_enter` and `gx_monitor_leave` macros delegate to platform primitives.

Dependencies:
- Includes `gpsync.h` for native synchronization types and operations.
- Includes `gsmemory.h` for allocator types.

Research notes:
- Semaphores initialize with count 0; monitors initialize as available/entered count 1.
- Performance matters here, so wait/signal and enter/leave are macros rather than wrapper functions.
