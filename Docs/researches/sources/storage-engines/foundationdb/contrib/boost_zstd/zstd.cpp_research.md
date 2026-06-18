# sources/storage-engines/foundationdb/contrib/boost_zstd/zstd.cpp

## Purpose
Implements Boost.Iostreams zstd filter support by adapting the zstd C streaming API (`ZSTD_CStream`, `ZSTD_DStream`, `ZSTD_inBuffer`, `ZSTD_outBuffer`) to the `boost::iostreams::detail::zstd_base` abstraction declared by Boost headers. It supplies compression defaults, status/flush constants, error wrapping, stream initialization, buffer handoff, and compressor/decompressor execution.

## Important APIs, Types, And Functions
The file defines constants in `boost::iostreams::zstd`: `best_speed`, `best_compression`, `default_compression`, `okay`, `stream_end`, and flush actions `finish`, `flush`, `run`. `zstd_error::check(size_t)` converts zstd error codes into Boost exceptions. `detail::zstd_base` owns opaque `cstream_`, `dstream_`, `in_`, and `out_` pointers, with methods `before`, `after`, `deflate`, `inflate`, `reset`, and `do_init`.

## Control Flow
Construction allocates one compression stream, one decompression stream, and one input/output buffer pair. `before()` maps Boost buffer pointer ranges into zstd buffer structs. `deflate()` compresses available input, then optionally flushes or ends the stream depending on the action. `inflate()` repeatedly calls `ZSTD_decompressStream()` while both input and output progress are possible to satisfy Boost's expectation around short reads. `after()` writes consumed/produced positions back to caller pointers. `reset()` and `do_init()` zero buffers and initialize the selected zstd stream.

## State And Persistence
State is in-memory only. `level` stores the selected compression level, and `eof_` tracks whether a finish action completed. No files or durable metadata are written.

## Dependencies And Integration
Depends on libzstd and Boost.Iostreams internals. It is compiled as part of the Boost zstd shim under FoundationDB contrib rather than FoundationDB runtime logic directly. Integration is through Boost filter classes in `<boost/iostreams/filter/zstd.hpp>`.

## Risks
The code assumes all zstd allocation calls succeed; null stream pointers are not checked before use. Custom allocator parameters to `do_init()` are accepted but ignored. `inflate()` returns stream status based on action and empty buffers rather than zstd frame completion result, so behavior is tied to Boost's filter contract. The compression `level` must be initialized before `reset(compress=true, realloc=true)` is meaningful.

## Test Signals
Useful tests are round-trip compression/decompression, flush and finish behavior with tiny output buffers, corrupt input error propagation, repeated reset/reuse, and empty-input finish handling.
