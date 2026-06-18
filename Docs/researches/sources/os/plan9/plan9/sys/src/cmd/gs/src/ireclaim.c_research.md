# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ireclaim.c

Interpreter interface to Ghostscript garbage collection and VM reclaim.

Key behavior:
- Installs `ireclaim` as `gs_imemory.reclaim` during initialization.
- `ireclaim` is called either for allocation-pressure GC (`space < 0`) or explicit `vmreclaim`.
- Locates the requesting memory space, resets allocation requests, chooses local versus global collection, and calls `gs_vmreclaim`.
- After allocation-pressure GC, checks total allocated memory against `max_vm` and returns `VMerror` if still over limit.
- `gs_vmreclaim` reconstructs `i_ctx_t` from embedded `gs_dual_memory_t`, stores context state, collects active memory spaces and stable-memory companions, closes allocator chunks, prepares allocators for GC, registers the context pointer as a root, invokes `GS_RECLAIM`, reloads context state, refreshes `systemdict`, cleans dictionary/name caches, and reopens chunks.
- Defines `ireclaim_l2_op_defs` with an init hook.

Notable dependencies:
- Context save/load from `icontext.h`.
- Save-state traversal via `isave.h` and `isstate.h`.
- Stack globals from `dstack.h`, `estack.h`, and `ostack.h`.

Research notes:
- Comments contain two explicit “ABORT IF code < 0” placeholders after context store/load, indicating incomplete failure handling.
- The code assumes `gs_dual_memory_t` is embedded inside context state at a known offset.
