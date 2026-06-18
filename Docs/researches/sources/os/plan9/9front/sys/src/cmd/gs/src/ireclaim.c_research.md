# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ireclaim.c

Interpreter interface to Ghostscript garbage collection.

Key behavior:
- Installs `ireclaim` as the interpreter allocator’s GC hook during initialization.
- `ireclaim` selects the VM space to collect based on allocator requests or explicit `vmreclaim` space, resets requested flags, runs `gs_vmreclaim`, resets allocation limits, and enforces `max_vm`.
- `gs_vmreclaim` recovers the interpreter context from the embedded `gs_dual_memory_t`, stores context state, closes allocation chunks, prepares file lists/allocation state for GC, registers the context root, invokes `GS_RECLAIM`, reloads relocated context state, updates `systemdict`, cleans up dictionary/name cached value pointers, and reopens chunks.
- Exports `ireclaim_l2_op_defs` with `op_def_end(ireclaim_init)`.

Notable dependencies:
- Memory/GC and context headers: `gsstruct.h`, `iastate.h`, `icontext.h`, `isave.h`, `isstate.h`.
- Stack headers: `dstack.h`, `estack.h`, `ostack.h`.
- `interp.h`, `opdef.h`, and `store.h`.

Research notes:
- The file assumes `gs_dual_memory_t` is embedded in `i_ctx_t` and recovers the context pointer with `offset_of`.
- Both normal VM spaces and stable-memory allocators are included in the memory list when needed.
- Comments mark unhandled failure cases after `context_state_store` and `context_state_load`.
- After collection, dictionary/name caches are explicitly refreshed with `dicts_gc_cleanup`.
