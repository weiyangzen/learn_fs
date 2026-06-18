# sources/sync-backup/rsync/zlib/zlib.h

Purpose: public API header for the rsync-vendored zlib 1.2.8 compression library. It defines the stable ABI used by deflate/inflate stream users, gzip file accessors, one-shot compression helpers, checksum routines, large-file variants, version checking macros, and selected undocumented/internal entry points.

Important APIs/types/functions: `z_stream` is the central caller-owned stream descriptor with input/output cursors, total counters, allocator hooks, opaque state, data type, and running checksum. `gz_header` models gzip metadata. Major exports include `deflate*`, `inflate*`, `inflateBack*`, `compress*`, `uncompress`, `gz*`, `adler32*`, `crc32*`, `zlibVersion`, `zlibCompileFlags`, and `zError`. Macros wrap `deflateInit`, `inflateInit`, `deflateInit2`, `inflateInit2`, and `inflateBackInit` to pass `ZLIB_VERSION` and `sizeof(z_stream)` for ABI validation.

Control flow: callers initialize a stream, repeatedly set `next_in`/`avail_in` and `next_out`/`avail_out`, call `deflate` or `inflate` until progress, completion, or error, then release with `deflateEnd` or `inflateEnd`. Flush constants control block boundaries and finishing behavior. Gzip helpers wrap similar state behind `gzFile` and expose open/read/write/seek/close/error operations.

State and persistence behavior: zlib keeps per-stream state behind `struct internal_state`, uses caller-provided or default allocators, updates `total_in`, `total_out`, `msg`, `data_type`, and `adler`, and persists gzip data only through `gz*` file APIs. The header also exposes 64-bit offset compatibility aliases depending on large-file macros.

Dependencies/integration: depends on `zconf.h` for platform typedefs, linkage attributes, `z_off_t`, and prefix/large-file configuration. In rsync this header forms the contract between bundled zlib sources and rsync compression code.

Risks/test signals: the file is ABI-sensitive; mismatched struct layout, version macros, `Z_PREFIX_SET`, or large-file aliasing can break callers. Correctness is normally signaled by zlib stream tests, gzip round trips, checksum vectors, and consumers checking for `Z_VERSION_ERROR`, `Z_STREAM_ERROR`, `Z_DATA_ERROR`, `Z_BUF_ERROR`, and `Z_STREAM_END`.
