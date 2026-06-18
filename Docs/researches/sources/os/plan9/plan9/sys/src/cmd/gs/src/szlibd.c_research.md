# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/szlibd.c

Purpose: zlib decompression stream filter.

Key contents:
- `s_zlibD_init` allocates dynamic state and calls `inflateInit2`, honoring `no_wrapper`.
- `s_zlibD_reset` calls `inflateReset`.
- `s_zlibD_process` maps Ghostscript stream cursors to `z_stream`, handles empty input/full output, detects a known empty-stream encoding from JAWS PDF output, and converts zlib statuses to stream statuses.
- `s_zlibD_release` calls `inflateEnd` and frees dynamic state.
- Exports `s_zlibD_template`.

Dependencies: `memory_.h`, `std.h`, `gsmemory.h`, `gsmalloc.h`, `strimpl.h`, `szlibxx.h`, zlib.

Integration notes: used as a decoding filter template in the stream framework.

Risks: several initialization/reset failures collapse to `ERRC` with comments noting this is imprecise; malformed input status reporting is therefore coarse.
