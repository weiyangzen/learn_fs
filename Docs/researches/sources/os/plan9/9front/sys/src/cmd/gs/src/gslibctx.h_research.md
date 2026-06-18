# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslibctx.h

Declares Ghostscript’s per-library memory context structure and initialization/accessor API.

Key structure:
- `gs_lib_ctx_t` holds:
  - owning `gs_memory_t *memory`
  - real/redirected stdio file pointers
  - stdout redirection flags
  - DLL/shared-library caller handle
  - stdin/stdout/stderr/poll callbacks
  - `gs_next_id` counter
  - `top_of_system`
  - interpreter name table pointer
  - `dict_auto_expand`

Key declarations:
- `int gs_lib_ctx_init(gs_memory_t *mem);`
- `void *gs_lib_ctx_get_interp_instance(gs_memory_t *mem);`
- `const gs_memory_t *gs_lib_ctx_get_non_gc_memory_t(void);`

Research notes:
- The comments acknowledge interpreter-specific fields living here as a hack.
- Context propagation depends on memory objects copying `gs_lib_ctx` into derived allocators.
