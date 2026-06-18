# sources/sync-backup/rsync/zlib/compress.c

Purpose: bundled zlib convenience API for compressing an in-memory buffer in one call and computing an upper bound for compressed size.

Important APIs/functions: `compress2()` initializes a `z_stream`, calls `deflateInit(level)`, runs `deflate(..., Z_FINISH)`, stores `stream.total_out` in `*destLen`, and calls `deflateEnd()`. `compress()` calls `compress2()` with `Z_DEFAULT_COMPRESSION`. `compressBound()` returns the standard conservative bound based on source length.

Control flow and state: no static state. The destination length is input/output: caller supplies capacity and receives actual compressed size. Errors distinguish invalid level/stream, memory failure, and insufficient output buffer (`Z_BUF_ERROR`).

Dependencies and integration: depends on bundled `zlib.h`/deflate implementation. Rsync’s `token.c` mainly uses streaming deflate directly, but this file is part of the bundled library surface and may be used by tools/tests or other zlib consumers. Risks are caller-supplied buffer sizing and 16-bit `MAXSEG_64K` truncation checks. Test signals are zlib API compatibility and compressed transfer integrity.
