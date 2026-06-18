# sources/sync-backup/casync/src/compressor.c

## Purpose

`compressor.c` is the streaming compression/decompression adapter for xz, gzip, and zstd chunk/archive handling. It normalizes optional library support and differing stream APIs into one `CompressorContext` interface with small status codes for EOF, more-output/more-input, and good progress.

## Important APIs, Types, and Functions

`detect_compression()` recognizes xz, gzip, and zstd magic bytes. It returns a `CaCompressionType`, `-EAGAIN` when the provided prefix is too short to decide, or `-EBADMSG` when enough bytes are present and no known signature matches. `compressor_is_supported()` maps compression enum values to compile-time `HAVE_LIBLZMA`, `HAVE_LIBZ`, and `HAVE_LIBZSTD`.

`compressor_start_decode()` and `compressor_start_encode()` validate compressor enum values, initialize the correct stream (`lzma_stream_decoder`, `inflateInit2`, `ZSTD_createDStream`, `lzma_easy_encoder`, `deflateInit2`, `ZSTD_createCStream`), set operation mode, and return `-ENOSYS` if the library was not compiled in.

`compressor_finish()` releases library stream state according to compressor and operation. `compressor_input()` stores the caller's input buffer in the selected stream. `compressor_decode()` and `compressor_encode()` write output into caller buffers, set `ret_done`, and return `COMPRESSOR_EOF`, `COMPRESSOR_MORE`, or `COMPRESSOR_GOOD`, or negative errno-style errors.

## Control Flow

The required sequence is initialize `CompressorContext` with `COMPRESSOR_CONTEXT_INIT`, start encode/decode, repeatedly call `compressor_input()` with available input, call encode/decode with output buffers until it reports good/more/eof, then finish. Decode paths reject trailing bytes after stream EOF as `-EBADMSG`. Encode paths use a `finalize` flag to select final stream operations (`LZMA_FINISH`, `Z_FINISH`, `ZSTD_endStream`) once input is exhausted.

## State and Persistence Behavior

All persistent state is in `CompressorContext`: current operation, compressor type, and the active library stream union. The adapter does not own the caller input/output buffers. `compressor_finish()` currently releases library resources but does not reset `operation` back to uninitialized, so contexts should not be reused without reinitialization discipline.

## Dependencies and Integration Points

The file depends on `compressor.h`, `cacompression.h`, optional liblzma/zlib/zstd headers, and `util.h` for assertions/macros. It is used by chunk/store/archive compression helpers such as `ca_compress()` and decompression readers.

## Risks and Edge Cases

The code asserts positive input/output availability in several decode paths; callers must not invoke decode with empty input or zero output size. zstd input/output buffer `.pos` fields are preserved across calls and must be correctly reset by `compressor_input()` and output setup. Missing optional libraries produce `-ENOSYS`; callers must handle unsupported configured compression. `compressor_is_supported()` uses `assert("Unknown compression type")`, which is a non-null string and therefore not an effective assertion failure; invalid enum handling relies more on start functions.

## Test Signals

Tests should round-trip xz/gzip/zstd when compiled in, detect magic prefixes including short buffers, reject trailing bytes after compressed streams, exercise zero/invalid arguments, compile with each optional library disabled, check `COMPRESSOR_MORE` for small output buffers, and validate finalize semantics for zstd streams with no pending input.
