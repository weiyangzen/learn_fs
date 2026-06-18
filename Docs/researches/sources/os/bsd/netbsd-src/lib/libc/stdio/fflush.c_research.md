# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fflush.c

Read completely: 120 lines.

This file implements `fflush` and internal `__sflush`. `fflush(NULL)` walks all open streams under `__sfp_lock`; single-stream flush validates write-capable state, then `__sflush` writes buffered bytes through the stream write hook and optionally calls a stream flush hook.

Important interactions: used by close, seek, cleanup, and write paths; `_fwalk(__sflush)` handles process-wide flushing.

Security/reliability notes: write failures set `__SERR` and return `EOF`; buffers are reset before invoking the write hook to tolerate longjmp or buffer replacement.
