# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslibctx.c

Implements the Ghostscript library context stored on `gs_memory_t`. `gs_lib_ctx_init` allocates a `gs_lib_ctx_t`, captures real process stdio, initializes stdout/stderr redirection state, DLL callback hooks, polling hook, per-context `gs_next_id`, and dictionary auto-expand policy.

`outwrite`, `errwrite`, `outflush`, and `errflush` centralize output routing. Output can go to redirected files, stderr, callback functions, or captured real stdout/stderr. Diagnostics use a file-static `mem_err_print`, so stderr handling is effectively process-global even though most context data is per-memory.

`gs_lib_ctx_get_non_gc_memory_t` exposes the non-GC allocator associated with the diagnostic memory context. The file is important for shared-library embedding and callback-based IO.
