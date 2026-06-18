# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_macpoll.c

Read status: complete.

Purpose: Mac polling/interrupt support for Ghostscript when `CHECK_INTERRUPTS` is enabled.

Main logic:
- Uses `TickCount` to throttle polling to roughly every few ticks.
- If legacy `pgsdll_callback` is installed, calls it with `GSDLL_POLL` and `hwndtext`.
- Otherwise, falls back to the newer `gs_lib_ctx->poll_fn` callback, obtaining non-GC memory context when `mem == NULL`.
- Returns the callback’s interrupt value or `0`.

Filesystem/storage relevance:
- None. This is event/poll integration.

Notable behavior:
- Comments explicitly warn that static state and the `mem == NULL` fallback are not thread-safe.
