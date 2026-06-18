# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mspol.c

Windows interpreter polling support.

Key behavior:
- When `CHECK_INTERRUPTS` is enabled, defines `gp_check_interrupts`.
- Uses the provided memory context, or falls back to `gs_lib_ctx_get_non_gc_memory_t`.
- Invokes `gs_lib_ctx->poll_fn(caller_handle)` if present.
- Returns `0` when no polling callback exists.

Notable dependencies:
- Ghostscript interpreter/library context headers: `iapi.h`, `iref.h`, `iminst.h`, `imain.h`.

Research notes:
- A comment marks the fallback memory lookup as a major non-thread-safe hack.
