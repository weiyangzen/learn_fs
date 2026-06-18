# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngrio.c

## Purpose

`pngrio.c` centralizes libpng read input. It provides the internal `png_read_data()` dispatcher, the default stdio/WinCE read implementation, legacy far-buffer support, and the public `png_set_read_fn()` hook for custom input sources.

This is vendored libpng I/O glue inside Plan 9 Ghostscript sources.

## Main Responsibilities

- Route all read requests through `png_ptr->read_data_fn`.
- Provide a default reader based on `fread()` or WinCE `ReadFile()`.
- Fail with `png_error()` on short reads or missing read callbacks.
- Support old memory models where far buffers must be copied through a near temporary buffer.
- Install custom read callbacks and clear conflicting write callbacks.

## Key Functions

`png_read_data(png_ptr, data, length)`:

- Logs a debug read size.
- Calls `png_ptr->read_data_fn`.
- Raises `png_error()` if the callback is `NULL`.

`png_default_read_data()`:

- When stdio is enabled, reads from `png_ptr->io_ptr`.
- Uses `ReadFile()` on `_WIN32_WCE`.
- Uses `fread()` otherwise.
- Requires the exact requested byte count.
- Raises `png_error()` on short read.

Legacy `USE_FAR_KEYWORD` variant:

- Converts far pointers when possible.
- If the target data pointer cannot be used directly by stdio, reads chunks into a 1024-byte near stack buffer and copies into the target.
- Checks total bytes read against requested length.

`png_set_read_fn(png_ptr, io_ptr, read_data_fn)`:

- Stores caller I/O state in `png_ptr->io_ptr`.
- Installs caller read callback, or default stdio reader when available and callback is `NULL`.
- If a write callback was already set on the same structure, clears it and warns because a `png_struct` must not be both read and write I/O.
- Clears output flush callback when write flush support is compiled.

## Dependencies

Uses definitions and callbacks from `png.h`:

- `png_structp`
- `png_rw_ptr`
- `png_FILE_p`
- `png_error()`
- `png_warning()`
- `png_memcpy()`
- platform conversion macros for far pointers

## Error Handling

Read failure is fatal. Callers using custom read functions are expected to call `png_error()` themselves when they cannot satisfy a read. The default implementation enforces exact-length reads.

## Research Notes

This file is intentionally narrow. Higher-level readers (`pngread.c` and `pngpread.c`) rely on this file so that libpng can be used over files, memory buffers, network streams, or application-specific stream abstractions without changing decode logic.
