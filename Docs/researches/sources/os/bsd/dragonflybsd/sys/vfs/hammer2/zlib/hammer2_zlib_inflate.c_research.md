# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/zlib/hammer2_zlib_inflate.c

Source read: complete file, 1052 lines.

Purpose: This is the HAMMER2-local zlib inflate implementation, adapted for DragonFly kernel use. It initializes and tears down inflate state, decodes zlib/raw deflate streams, builds or references fixed Huffman tables, maintains the sliding output window, verifies Adler checksums, and exposes the usual zlib inflate entry points with `Z_PREFIX` name remapping through the included headers.

Key interfaces:
- `inflateInit2_()` allocates `struct inflate_state` with `kmalloc(..., C_ZLIB_BUFFER_INFLATE, M_INTWAIT)`, validates `ZLIB_VERSION` and `sizeof(z_stream)`, and delegates to `inflateReset2()`.
- `inflateResetKeep()`, `inflateReset()`, and `inflateReset2()` reset stream counters, wrap/window settings, code-table pointers, bit accumulator state, distance sanity, and dictionary flags.
- `inflatePrime()` injects bits into the input accumulator or clears it when called with negative bit count.
- `inflate()` is the main state machine for headers, block type dispatch, stored blocks, fixed blocks, dynamic code tables, literal/length/distance decoding, match copying, trailer verification, and return-code selection.
- `inflateEnd()` releases the optional sliding window and the inflate state with the same DragonFly malloc type.

Implementation notes:
- Only zlib wrapping is meaningfully implemented in the state machine despite enum support for gzip modes in the header; the header path checks the zlib CMF/FLG modulus, method, window size, optional dictionary id, and Adler trailer.
- `fixedtables()` normally includes `hammer2_zlib_inffixed.h`; when `BUILDFIXED` is enabled it generates fixed tables at first use, with comments warning about thread safety.
- `updatewindow()` lazily initializes the circular window only when needed and copies at most the last window-sized suffix of output.
- `inflate()` uses local register-style variables and macros (`LOAD`, `RESTORE`, `NEEDBITS`, `BITS`, `DROPBITS`, `BYTEBITS`) to minimize repeated stream/state memory accesses.
- Dynamic block handling reads `nlen`, `ndist`, and `ncode`, builds the code-length tree with `inflate_table(CODES, ...)`, expands repeat codes 16/17/18 into `state->lens`, then builds literal/length and distance decode tables.
- Fast path handoff to `inflate_fast(strm, out)` occurs when at least six input bytes and 258 output bytes are available.

Integration:
- Depends on `hammer2_zlib_zutil.h`, `hammer2_zlib_inftrees.h`, `hammer2_zlib_inflate.h`, `hammer2_zlib_inffast.h`, and `../hammer2.h`.
- Uses DragonFly `MALLOC_DECLARE`/`MALLOC_DEFINE` and `kmalloc`/`kfree` rather than the stock zlib allocator hooks.
- Consumes `adler32()`, `inflate_table()`, and the `code` layout defined in companion zlib files.

Risks and review notes:
- `updatewindow()` assumes `state->window` is already allocated before writing to it, but this file initializes `state->window` to `Z_NULL` and does not allocate it in `updatewindow()` before `zmemcpy()`. Stock zlib normally allocates the window when first needed; this HAMMER2 copy should be checked against its callers and local patches.
- The `inflate_state` enum includes gzip modes, but `inflate()` does not implement gzip header/trailer processing; callers expecting gzip wrapper support would fail or misinterpret data.
- `INFLATE_ALLOW_INVALID_DISTANCE_TOOFAR_ARRR` can synthesize zero bytes for invalid distances if enabled; default `state->sane = 1` rejects those streams.
- Error paths report string literals through `strm->msg`; kernel callers should not assume ownership.
