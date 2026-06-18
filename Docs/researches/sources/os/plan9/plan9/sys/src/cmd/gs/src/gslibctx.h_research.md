# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gslibctx.h

Defines `gs_lib_ctx_t`, the per-library/per-memory context used by Ghostscript embedding code. It stores stdio streams, redirected stdout stream, redirection flags, interactive-stdin flag, caller handle, stdin/stdout/stderr/poll callbacks, next-id counter, interpreter/system hooks, PostScript name table pointer, and dictionary auto-expand policy.

Declares `gs_lib_ctx_init`, `gs_lib_ctx_get_interp_instance`, and `gs_lib_ctx_get_non_gc_memory_t`. The comments note some fields are legacy or interpreter-specific hacks rather than clean library-context state.
