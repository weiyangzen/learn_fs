# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngwio.c

## Summary

`pngwio.c` contains libpng 1.2.8 write-side I/O glue. It routes encoded PNG bytes to user-provided callbacks or to default stdio-backed writers, and optionally flushes pending output.

This is not filesystem or storage code. It is third-party PNG library I/O abstraction code vendored in Plan 9's Ghostscript tree.

## Main Compile-Time Gates

The file is active under `PNG_WRITE_SUPPORTED`.

Other gates:

- `PNG_NO_STDIO`: removes default stdio write/flush implementations.
- `_WIN32_WCE`: uses `WriteFile` instead of `fwrite`.
- `USE_FAR_KEYWORD`: enables old segmented-memory handling for far buffers.
- `PNG_WRITE_FLUSH_SUPPORTED`: enables explicit flush support.

## Entry Points

- `png_write_data(png_structp png_ptr, png_bytep data, png_size_t length)`: private central output function. Calls `png_ptr->write_data_fn` or raises a fatal libpng error if no writer is set.
- `png_default_write_data(...)`: default writer using `fwrite` or Windows CE `WriteFile`.
- `png_flush(png_structp png_ptr)`: private flush dispatcher, when flush support is enabled.
- `png_default_flush(png_structp png_ptr)`: default stdio flush using `fflush`.
- `png_set_write_fn(png_structp png_ptr, png_voidp io_ptr, png_rw_ptr write_data_fn, png_flush_ptr output_flush_fn)`: public API for installing custom write and flush callbacks.
- `png_far_to_near(...)`: legacy segmented-memory conversion helper under `USE_FAR_KEYWORD`.

## I/O Model

`png_set_write_fn` stores the caller's `io_ptr`, chooses either the provided callbacks or default stdio callbacks, and clears any read callback already set on the same `png_struct`.

This is libpng's callback boundary between encoder logic and the embedding application. Higher-level chunk and row-writing routines call `png_write_data`; they do not write directly to files.

## Error Handling

Write failures are fatal libpng errors:

- If no writer is configured, `png_write_data` calls `png_error`.
- If `fwrite` or `WriteFile` writes fewer bytes than requested, `png_default_write_data` calls `png_error`.
- In far-buffer mode, failed pointer conversion or short writes are also fatal.

## Legacy / Portability Notes

The `USE_FAR_KEYWORD` branch supports old memory models where standard I/O cannot write far buffers directly. It copies data into a 1024-byte near stack buffer in chunks before writing.

The Windows CE path uses `WriteFile` because normal stdio support is unavailable or unsuitable there.

## Dependencies

This file depends on internal libpng fields:

- `png_ptr->io_ptr`
- `png_ptr->write_data_fn`
- `png_ptr->output_flush_fn`
- `png_ptr->read_data_fn`

It also uses `png_error`, `png_warning`, `png_memcpy`, and pointer-conversion macros from libpng.

## Research Notes

The file is small but important because it is the sole default write-output abstraction for this libpng copy. Behavior is straightforward: install callbacks, write bytes, flush when requested, and prevent accidental simultaneous read/write callback use in the same structure.
