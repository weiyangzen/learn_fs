# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemlok.h

Interface for monitor-locked memory allocator wrapper.

Key structure:
- `gs_memory_locked_t` embeds `gs_memory_common`, target allocator pointer, and monitor pointer.

Key declarations:
- `gs_memory_locked_init`
- `gs_memory_locked_release`
- `gs_memory_locked_target`

Research notes:
- The header states that `free_all` with `FREE_ALL_DATA` is a no-op because the wrapper does not own or track target allocations.
