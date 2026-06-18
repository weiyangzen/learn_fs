# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gslibctx.c

Implements Ghostscript library context initialization and central stdout/stderr routing.

Key behavior:
- Captures real `stdin`, `stdout`, and `stderr` before Ghostscript headers may redefine them.
- Keeps a static `mem_err_print` memory pointer used for stderr context lookup.
- `gs_lib_ctx_get_non_gc_memory_t` returns the non-GC allocator from `mem_err_print`, if available.
- `gs_lib_ctx_init` creates one `gs_lib_ctx_t` per memory root, stores it in `mem->gs_lib_ctx`, initializes stdio fields, callback slots, poll hook, ID counter, and dictionary auto-expand flag.
- `outwrite` routes stdout to redirected file, stderr, callback, or real stdout, then flushes.
- `errwrite` routes stderr to callback or real stderr, then flushes.
- `outflush` and `errflush` flush only when output is not callback-managed.

Dependencies:
- Uses `gslibctx.h` and `gsmemory.h`.
- Uses allocator-provided `gs_alloc_bytes_immovable` during context setup.

Research notes:
- `mem_err_print` is global/static, so stderr routing depends on the most recent initialized memory context.
- This file is API-embedding glue for DLL/shared-object style callers.
