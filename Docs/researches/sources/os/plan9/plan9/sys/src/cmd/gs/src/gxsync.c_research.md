# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxsync.c

Implementation of Ghostscript synchronization primitive allocation wrappers.

Key behavior:
- `gx_semaphore_alloc` computes the real allocation size from `gp_semaphore_sizeof`, chooses movable or immovable allocation based on `gp_semaphore_open(0)`, stores the allocator, and initializes the native semaphore.
- `gx_semaphore_free` closes the native semaphore and frees the wrapper through its recorded allocator.
- `gx_monitor_alloc` does the same for monitor objects using `gp_monitor_sizeof` and `gp_monitor_open`.
- `gx_monitor_free` closes and frees a monitor.
- Wait/signal and enter/leave are macro wrappers in the header, redefined here to check consistency.

Notable dependencies:
- Platform synchronization API: `gpsync.h` via `gxsync.h`.
- Ghostscript allocator APIs: `gsmemory.h`, `memory_.h`.

Research notes:
- The native platform object has implementation-defined size, so the wrapper structs carry a placeholder native field and allocate adjusted byte counts.
- The allocation path handles platforms whose native synchronization objects cannot be moved by using immovable memory.
