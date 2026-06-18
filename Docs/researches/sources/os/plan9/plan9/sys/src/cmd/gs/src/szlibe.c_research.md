# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibe.c

Purpose: zlib compression stream filter.

Key contents:
- `s_zlibE_init` allocates dynamic state and calls `deflateInit2` with level, method, wrapper, memory level, and strategy.
- `s_zlibE_reset` calls `deflateReset`.
- `s_zlibE_process` maps stream cursors to zlib input/output buffers and uses `Z_FINISH` on final input, otherwise `Z_NO_FLUSH`.
- `s_zlibE_release` calls `deflateEnd` and frees dynamic state.
- Exports `s_zlibE_template`.

Dependencies: `std.h`, `gsmemory.h`, `gsmalloc.h`, `strimpl.h`, `szlibxx.h`, zlib.

Integration notes: used as an encoding filter template in the stream pipeline.

Risks: like the decoder, setup/reset errors return generic `ERRC`; init failure after `deflateInit2` does not explicitly free dynamic state in that branch.
