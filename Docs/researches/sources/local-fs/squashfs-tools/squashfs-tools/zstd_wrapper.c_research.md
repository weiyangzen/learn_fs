# File Research: sources/local-fs/squashfs-tools/squashfs-tools/zstd_wrapper.c

## Purpose

`zstd_wrapper.c` implements the Squashfs compressor adapter for Zstandard. It exposes a `zstd` compressor through `struct compressor zstd_comp_ops` and supports one compressor-specific option: `-Xcompression-level`.

The file handles option parsing, compressor-option serialization, append-mode option restoration, display, compression-context allocation, compression, decompression, and usage text.

## Main State

The file has one process-global compressor option:

- `compression_level`, initialized to `ZSTD_DEFAULT_COMPRESSION_LEVEL`.

`ZSTD_DEFAULT_COMPRESSION_LEVEL` is defined in `zstd_wrapper.h` as `15`, which is higher than the zstd library’s generic default and is the Squashfs tool default for this adapter.

## Option Parsing

`zstd_options(char *argv[], int argc)` recognizes:

- `-Xcompression-level <compression-level>`

Return contract matches the Squashfs compressor option interface:

- `1`: recognized and consumed one argument.
- `-1`: unrecognized option.
- `-2`: recognized but invalid or missing argument.

Accepted levels are:

- Negative fast-mode levels from `ZSTD_minCLevel()` through `-1`.
- Positive compression levels from `1` through `ZSTD_maxCLevel()`.

Level `0` is rejected explicitly. The parser uses `atoi()`, so non-numeric strings that convert to `0` are rejected, but strings with numeric prefixes and trailing junk would be accepted according to `atoi()` behavior.

## Filesystem Option Serialization

`zstd_dump_options(int block_size, int *size)` returns `NULL` when `compression_level` equals `ZSTD_DEFAULT_COMPRESSION_LEVEL`, meaning no compressor option block is needed for default settings.

For non-default levels, it fills a static `struct zstd_comp_opts` with `compression_level`, byte-swaps it through `SQUASHFS_INSWAP_COMP_OPTS()`, sets `*size`, and returns the structure pointer.

The `block_size` parameter is unused for zstd option serialization.

## Append-Mode Option Extraction

`zstd_extract_options(int block_size, void *buffer, int size)` restores compressor state from stored Squashfs compressor options.

If `size == 0`, it resets `compression_level` to `ZSTD_DEFAULT_COMPRESSION_LEVEL`. This is intentional for append mode: existing filesystem compressor options override any new command-line `-X` options.

For stored options, it requires `size >= sizeof(*comp_opts)`, byte-swaps the struct, validates that the stored level is nonzero and within the current zstd library’s min/max range, then assigns `compression_level`.

Using `size >= sizeof(*comp_opts)` allows larger option payloads to be accepted if future-compatible trailing data exists.

## Display

`zstd_display_options(void *buffer, int size)` validates and prints the stored compression level. It uses the same size and compression-level validity checks as extraction, then prints:

- `compression-level <level>`

Invalid stored options print an error message.

## Initialization

`zstd_init(void **strm, int block_size, int datablock)` creates a `ZSTD_CCtx` compression context with `ZSTD_createCCtx()`. On allocation failure it prints an error and returns `-1`; otherwise it stores the context in `*strm`.

`block_size` and `datablock` are unused. There is no separate metadata/data-block tuning in this wrapper.

The file does not define a cleanup callback in `zstd_comp_ops`, so context lifetime and cleanup are handled by the broader compressor framework if supported elsewhere, or the process lifetime.

## Compression

`zstd_compress(void *strm, void *dest, void *src, int size, int block_size, int *error)` calls:

- `ZSTD_compressCCtx((ZSTD_CCtx*)strm, dest, block_size, src, size, compression_level)`

The destination capacity is `block_size`, matching the Squashfs convention that compressed output must fit within the uncompressed block-size buffer.

If zstd returns an error, the wrapper returns `0`, treating all zstd compression errors as “not enough output space”. The comment explains this is because zstd error codes are not treated as stable enough for precise handling in this interface.

On success it returns the compressed byte count.

## Decompression

`zstd_uncompress(void *dest, void *src, int size, int outsize, int *error)` calls `ZSTD_decompress(dest, outsize, src, size)`.

On zstd error:

- It prints the output and input sizes to stderr.
- It stores `ZSTD_getErrorCode(res)` in `*error`.
- It returns `-1`.

On success it returns the decompressed byte count. The function does not separately verify that the result equals `outsize`; it trusts zstd’s return value and the caller’s expected-size handling.

## Usage and Option Arity

`zstd_usage()` documents the accepted compression-level range using runtime values from `ZSTD_minCLevel()` and `ZSTD_maxCLevel()`, including the default `15`. It notes that negative levels correspond to zstd `--fast`.

`option_args()` reports that `-Xcompression-level` consumes one argument.

## Registered Compressor

`zstd_comp_ops` registers:

- `.id = ZSTD_COMPRESSION`
- `.name = "zstd"`
- `.supported = 1`

and supplies init, compress, uncompress, option parsing, dump/extract/display, usage, and option-arity callbacks.

## Research Notes

This file is intentionally small compared with the XZ wrapper. It maps Squashfs’s compressor interface onto zstd’s context API and persists only the compression level. The main behavioral compatibility point is that stored compression levels are validated against the currently linked zstd library’s min/max range, so an image created with a level unsupported by the current library will be rejected during append/display.
