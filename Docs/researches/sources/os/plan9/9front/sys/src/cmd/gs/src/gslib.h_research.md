# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslib.h

Public library initialization/finalization interface.

Key declarations:
- `int gs_lib_init(FILE *debug_out);`
- `gs_memory_t *gs_lib_init0(FILE *debug_out);`
- `int gs_lib_init1(gs_memory_t *);`
- `void gs_lib_finit(int exit_status, int code, gs_memory_t *);`

Behavior contract:
- `gs_lib_init` performs complete initialization using the C heap.
- Clients needing a custom default allocator can call `gs_lib_init0`, adjust allocator setup, then call `gs_lib_init1`.
- `gs_lib_finit` performs cleanup after execution.

Research notes:
- Requires stdio and Ghostscript memory types.
- This header defines the lifecycle boundary used by the test harness and embedders.
