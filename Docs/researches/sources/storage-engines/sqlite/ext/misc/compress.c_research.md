# sources/storage-engines/sqlite/ext/misc/compress.c

## Purpose

`compress.c` provides scalar SQL functions `compress(X)` and `uncompress(X)` using zlib. The format is zlib-compressed payload prefixed by a SQLite-extension-specific variable-length integer containing the original uncompressed byte count.

## Important APIs, types, and functions

`sqlite3_compress_init()` registers `compress` as innocuous and `uncompress` as innocuous and deterministic. `compressFunc()` obtains the input blob and byte count from `sqlite3_value_blob()` and `sqlite3_value_bytes()`, encodes the original length in one to five 7-bit chunks, calls zlib `compress()`, and returns a blob allocated with `sqlite3_malloc64()`. `uncompressFunc()` decodes the size prefix, allocates the expected output buffer, calls zlib `uncompress()`, and returns the restored blob.

## Control flow

Compression computes a conservative zlib output bound, allocates `nOut+5`, emits the length prefix with the high bit set on the final prefix byte, then compresses after the prefix. Decompression reads up to five prefix bytes, accumulating seven bits per byte until a byte with bit `0x80` is seen; the remaining bytes are passed to zlib along with the decoded output size.

## State and persistence

The extension is stateless. It does not persist metadata outside the returned blob. The original size is embedded in the compressed value, so decompression does not need an external length.

## Dependencies and integration points

It depends on zlib headers and library symbols. The file notes that SQLAR and ZIP also use deflate variants, but this wrapper is not byte-compatible with ZIP or SQLAR because of its custom size prefix.

## Risks

Malformed inputs generally result in a NULL return because zlib errors free the buffer without setting an explicit SQLite error. If the size prefix is absent, `nOut` may be derived from the first bytes anyway and can lead to allocation attempts before zlib rejects the stream. Length handling uses `unsigned int`, so extremely large SQLite values depend on platform limits. The functions do not special-case SQL NULL input beyond SQLite's blob/bytes behavior.

## Test signals

Good coverage round-trips empty, text, binary with embedded NULs, and large blobs; verifies deterministic output for the same input and NULL/error behavior for malformed blobs, truncated prefixes, and non-zlib payloads.
