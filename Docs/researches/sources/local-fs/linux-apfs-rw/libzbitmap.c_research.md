# File Research: sources/local-fs/linux-apfs-rw/libzbitmap.c

## Purpose
Provides an in-kernel decompressor for APFS LZBITMAP/ZBM compressed payloads, ported from `libzbitmap` with decompression-only support.

## Main Responsibilities
- Validates the `ZBM\x09` stream magic.
- Iterates chunk headers with 24-bit compressed and decompressed lengths.
- Handles uncompressed chunks by copying payload bytes directly.
- Handles compressed chunks using bitmap metadata regions, nibble-coded bitmap selectors, repetition counts, and periodic back-references.
- Tracks total output length and supports a NULL destination mode for length discovery.

## Key Functions
- `zbm_decompress()`: public entry point; validates magic, decodes chunks until a zero-length final chunk, and returns decompressed length.
- `zbm_handle_chunk()`: reads chunk lengths, bounds-checks source/destination, and dispatches compressed vs uncompressed handling.
- `zbm_handle_compressed_chunk()`: initializes metadata pointers, reads bitmap tables, and expands the chunk.
- `zbm_apply_bitmap()`: emits literal bytes or repeats bytes from the current period.
- `zbm_read_bitmaps()` / `zbm_read_single_bitmap()`: parse trailing bitmap table entries.

## Dependencies
Uses kernel `errno`, `string.h`, and the local `libzbitmap.h` API. It is used by `compress.c` for APFS compressed-resource decoding.

## Notes
The decoder is defensive about malformed input: it checks source bounds, destination capacity, maximum decompressed chunk size, invalid periods, corrupt repetitions, and malformed free-running bitmap lists.
