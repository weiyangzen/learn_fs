# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_macpoll.c

Mac platform polling and interrupt callback support.

Key behavior:
- When `CHECK_INTERRUPTS` is enabled, defines `gp_check_interrupts`.
- Throttles polling using `TickCount`, only yielding after more than two ticks.
- Calls the deprecated `pgsdll_callback` poll path if present, passing `hwndtext`.
- Otherwise falls back to the newer `gs_lib_ctx->poll_fn` callback.

Notable dependencies:
- Carbon or Classic Mac timer headers.
- Ghostscript interpreter/library context headers.

Research notes:
- Comments warn that static state and fallback global memory lookup are not thread-safe.
