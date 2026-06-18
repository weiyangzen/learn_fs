# sources/storage-engines/sqlite/ext/misc/sqlar.c

## Purpose
Provides `sqlar_compress(X)` and `sqlar_uncompress(X,SZ)`, helper SQL functions used by SQLite's SQL archive support to store and restore zlib-compressed file payloads.

## Important APIs, Types, And Functions
`sqlarCompressFunc()` uses zlib `compressBound()` and `compress()` against BLOB input. `sqlarUncompressFunc()` uses zlib `uncompress()` with caller-supplied uncompressed size. `sqlite3_sqlar_init()` registers both functions as UTF-8 innocuous scalar functions.

## Control Flow
Compression only attempts zlib compression for BLOB values. If allocation fails it reports `SQLITE_NOMEM`; if zlib fails it reports an SQL error; if compressed output is not smaller than the original, it returns the original value. Uncompression returns the original value when `SZ<=0` or `SZ` equals the input byte length, otherwise it allocates `SZ` bytes and calls `uncompress()`.

## State And Persistence Behavior
The extension keeps no durable state. It transforms values for SQL statements. Persistence happens only when callers store returned blobs in an SQLar table.

## Dependencies And Integration Points
Depends on `sqlite3ext.h`, SQLite result/value/memory APIs, and zlib. It is integrated by the shell and any application that loads the extension and calls the functions.

## Risks And Edge Cases
`SZ` is trusted as the expected uncompressed size and is cast to zlib's `uLongf`; extremely large values can fail allocation or be problematic on platforms where zlib length types are narrower. Corrupt compressed data returns an SQL error. Non-BLOB compression inputs pass through unchanged, which preserves SQL type but may surprise callers expecting BLOB-only output.

## Test Signals
Tests should cover round trips, incompressible data pass-through, non-BLOB values, `SZ<=0`, `SZ==input size`, corrupt compressed blobs, very large size requests, and builds without zlib linkage.
