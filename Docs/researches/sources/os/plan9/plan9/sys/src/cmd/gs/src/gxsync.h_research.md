# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsync.h

Internal synchronization abstraction header for Ghostscript.

Key contents:
- Defines `gx_semaphore_t`, storing the allocator and a platform `gp_semaphore` native object. The comment notes the native field must be last because its actual size is platform-dependent.
- Declares `gx_semaphore_alloc` and `gx_semaphore_free`.
- Defines `gx_semaphore_wait` and `gx_semaphore_signal` as direct macros to platform operations.
- Defines `gx_monitor_t`, storing allocator and platform `gp_monitor`.
- Declares `gx_monitor_alloc` and `gx_monitor_free`.
- Defines `gx_monitor_enter` and `gx_monitor_leave` as macro wrappers.

Notable dependencies:
- `gpsync.h` for platform primitives.
- `gsmemory.h` for allocator types.

Research notes:
- Semaphores are documented as queued counting semaphores initialized with event count 0.
- Monitors are documented as initialized with event count 1, so the first enter succeeds immediately.
