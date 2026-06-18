# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmemraw.h

Historical raw-memory allocator interface, currently disabled with `#if 0`.

Key contents:
- Explains that `gsmemraw` used to be an abstract base class.
- States it is no longer in use; `gs_memory_t` is now the concrete base class because the full allocator interface must be available throughout the system.
- The disabled block contains older raw allocator status/types/procedure macros and comments about alignment requirements.
- Ends with only include guards active.

Research notes:
- No active API is exported beyond the include guard.
- Useful for understanding allocator design history and why raw allocation was folded into `gs_memory_t`.
