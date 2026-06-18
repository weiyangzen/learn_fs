# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_mspol.c

Read status: complete.

Purpose: Microsoft Windows polling support for Ghostscript interpreter builds.

Main logic:
- Under `CHECK_INTERRUPTS`, `gp_check_interrupts` uses the passed `gs_memory_t` context, or falls back to `gs_lib_ctx_get_non_gc_memory_t` when `mem == NULL`.
- If a `poll_fn` is registered in the library context, calls it with `caller_handle`.
- Returns `0` when no polling callback is available.

Filesystem/storage relevance:
- None. This is interrupt/event integration.

Notable behavior:
- Source comments call the `mem == NULL` fallback a major hack and not multithread-safe.
