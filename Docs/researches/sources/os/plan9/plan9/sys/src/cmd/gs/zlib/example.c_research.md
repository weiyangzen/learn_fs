# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/zlib/example.c

## Purpose
Provides a standalone zlib usage and regression example covering compression, decompression, gzip file I/O, flushing, sync recovery, large streams, dynamic parameter changes, and preset dictionaries.

## Public Surface
Test functions:
- `test_compress`, `test_gzio`, `test_deflate`, `test_inflate`.
- `test_large_deflate`, `test_large_inflate`.
- `test_flush`, `test_sync`.
- `test_dict_deflate`, `test_dict_inflate`.
- `main`.

## Implementation Notes
- Uses repeated `hello` data and a `hello` preset dictionary.
- `CHECK_ERR` exits on non-`Z_OK` return codes.
- `test_gzio` writes/reads `foo.gz` or platform-specific name, exercising `gzopen`, `gzputc`, `gzputs`, `gzprintf`, `gzseek`, `gztell`, `gzgetc`, `gzungetc`, and `gzgets`.
- Small-buffer deflate/inflate tests force one-byte input/output availability.
- Large tests exercise greedy compression, already compressed input, `deflateParams`, and output discard loops.
- Flush/sync tests intentionally corrupt a compressed block, then use `inflateSync`.
- Dictionary tests verify `Z_NEED_DICT`, Adler dictionary ID matching, and `inflateSetDictionary`.
- `main` checks zlib version compatibility, prints compile flags, allocates buffers, runs all tests, and frees memory.

## Dependencies
Uses public `zlib.h`, C stdio/string/stdlib, gzip file APIs, and allocation/free from libc.

## Risks and Notes
- Creates a gzip test file in the current directory.
- Exits process on first failure; not a library component.
- Filesystem relevance: limited to gzip file I/O test coverage.
