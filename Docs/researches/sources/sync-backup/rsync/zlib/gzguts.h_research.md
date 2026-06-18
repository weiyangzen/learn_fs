# sources/sync-backup/rsync/zlib/gzguts.h

Purpose: private header for zlib `gz*` file I/O internals. It centralizes portability includes, large-file setup, stdio/error adapters, default gzip buffer sizes, gzip read/write mode constants, and the internal `gz_state` object used by gzlib/gzread/gzwrite-style modules.

Important APIs/types/functions: defines `ZLIB_INTERNAL` visibility when hidden symbols are available, `local`, `GZBUFSIZE`, mode constants `GZ_NONE`, `GZ_READ`, `GZ_WRITE`, `GZ_APPEND`, and read-state constants `LOOK`, `COPY`, `GZIP`. The key type is `gz_state`, which embeds the public `gzFile_s` prefix and stores fd/path, buffers, transparent/direct flag, read header state, compression settings, seek state, error state, and an in-place `z_stream`. It declares shared helpers `gz_error`, optionally `gz_strwinerror`, and `gz_intmax`.

Control flow: this header does not implement algorithms, but it defines the state machine vocabulary used by gzip file readers: `LOOK` searches for a gzip header, `COPY` passes transparent input through, and `GZIP` inflates compressed data. It also maps Windows/CE/POSIX file functions and snprintf/vsnprintf availability so the gz modules compile on many targets.

State and persistence: `gz_state` persists for an open gzip file handle. It owns heap buffers, fd position metadata, eof/past flags, deferred seek information, error messages, and an embedded inflate/deflate stream. The `x` member is intentionally first/exposed for `gzgetc()` macro access to `have`, `next`, and `pos`.

Dependencies and integration points: includes `zlib.h`, stdio/string/stdlib/limits/fcntl/io headers depending on platform, and relies on zlib allocator and stream APIs. It is consumed by gz file implementation files, not by the deflate/inflate bit-level core directly.

Risks: platform preprocessor branches are high risk because small changes can alter ABI/export visibility, large-file offsets, Windows function mapping, or availability of safe formatting functions. `gz_state` layout matters for macros that treat the beginning as `gzFile_s`. Error-message ownership must stay consistent with `gz_error` cleanup.

Test signals: build on POSIX and Windows-like configurations, with and without large-file flags, hidden visibility, and `NO_GZCOMPRESS`. Runtime tests should cover gzopen/gzdopen, transparent reads, gzip reads/writes, seeks, errors, and files larger than 2 GiB when large-file support is enabled.
