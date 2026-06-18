# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngpread.c

## Role

`pngpread.c` implements progressive, push-mode PNG reading for libpng 1.2.8. Instead of pulling from a file stream, callers feed arbitrary byte buffers via `png_process_data()`, and this file preserves partial state across calls until enough data exists to parse signatures, chunks, IDAT streams, rows, text chunks, and end markers.

## Main APIs and Behavior

- `png_process_data()` appends/restores the caller-provided input buffer and repeatedly processes available data.
- `png_process_some_data()` dispatches by `png_ptr->process_mode`.
- `png_push_read_sig()` reads and validates the PNG signature incrementally.
- `png_push_read_chunk()` parses chunk headers and dispatches known chunks:
  - Critical: `IHDR`, `PLTE`, `IDAT`, `IEND`.
  - Ancillary: `gAMA`, `sBIT`, `cHRM`, `sRGB`, `iCCP`, `sPLT`, `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, `pCAL`, `sCAL`, `tIME`, `tEXt`, `zTXt`, `iTXt`, plus unknown chunks.
- `png_push_read_IDAT()` consumes IDAT chunk data progressively, calculates CRC, and feeds compressed bytes to zlib.
- `png_process_IDAT_data()` runs `inflate()` and emits complete rows.
- `png_push_process_row()` filters, copies, transforms, interlace-expands, and emits row callbacks.
- `png_read_push_finish_row()` advances row/pass counters for Adam7 interlacing.
- `png_push_handle_tEXt()`, `png_push_read_tEXt()`, `png_push_handle_zTXt()`, `png_push_read_zTXt()`, `png_push_handle_iTXt()`, and `png_push_read_iTXt()` handle progressive text chunks.
- `png_push_handle_unknown()` handles unknown critical/ancillary chunks and optional user callbacks.
- `png_set_progressive_read_fn()` installs progressive info, row, and end callbacks.
- `png_progressive_combine_row()` lets applications combine interlaced rows into an existing output row.

## Progressive Buffer Model

The file maintains two input regions:

- `current_buffer`: bytes from the most recent caller buffer.
- `save_buffer`: previously received bytes that were insufficient to finish a parse step.

Core helpers:

- `png_push_fill_buffer()` copies requested bytes from saved/current buffers and advances buffer pointers.
- `png_push_save_buffer()` compacts saved bytes, grows `save_buffer` when needed, copies remaining current bytes into it, and marks current input consumed.
- `png_push_restore_buffer()` initializes buffer pointers for a new `png_process_data()` call.

This is the core mechanism that lets chunk headers, CRC tails, and text payloads span caller buffer boundaries.

## IDAT and Row Flow

Once `IDAT` is found:

1. `png_push_read_chunk()` validates `IHDR`/`PLTE` ordering.
2. It sets `idat_size`, marks `PNG_HAVE_IDAT`, switches to `PNG_READ_IDAT_MODE`, calls the info callback, and primes zlib output to `row_buf`.
3. `png_push_read_IDAT()` consumes compressed data from saved/current buffers, updates CRC, and calls `png_process_IDAT_data()`.
4. `png_process_IDAT_data()` inflates until a row is complete or input is exhausted.
5. `png_push_process_row()` applies PNG filtering, copies `row_buf` to `prev_row`, applies read transformations, handles interlace expansion, and invokes the row callback.

## Dependencies

- Chunk handlers from the broader libpng reader (`png_handle_IHDR`, `png_handle_PLTE`, etc.).
- CRC helpers: `png_reset_crc`, `png_crc_read`, `png_crc_finish`, `png_calculate_crc`.
- zlib `inflate()` and `inflateReset()`.
- Transform helpers from `pngrtran.c`, especially `png_do_read_transformations()` and `png_do_read_interlace()`.
- User callback fields in `png_struct`.

## State Mutated

- `process_mode`, `mode`, `flags`.
- `buffer_size`, `current_buffer_*`, `save_buffer_*`.
- `push_length`, `skip_length`, `idat_size`.
- zlib stream fields.
- row state: `row_number`, `pass`, `iwidth`, `irowbytes`, `num_rows`, `row_info`.
- text state: `current_text`, `current_text_ptr`, `current_text_size`, `current_text_left`.

## Risks and Maintenance Notes

- The push parser is stateful and sensitive to exact buffer accounting. Any change to `buffer_size`, `save_buffer_size`, or `current_buffer_size` must preserve all three invariants.
- `png_push_save_buffer()` grows the saved buffer with overflow protection against `PNG_SIZE_MAX`, which is important for adversarial chunk boundaries.
- Signature validation contains a legacy branch using `num_to_check - 4`; behavior should be reviewed carefully if extremely small progressive buffers are expected.
- Text chunk handling allocates full chunk buffers before parsing. Large text chunks are only constrained under `PNG_MAX_MALLOC_64K`.
- `zTXt` decompression repeatedly reallocates and copies accumulated text, which is simple but can be expensive for large compressed text.
- Unknown critical chunks are fatal unless configured/user-handled.

## Research Summary

This file is the asynchronous counterpart to `pngread.c`. It implements the same PNG parse semantics but breaks every operation into resumable states, with callbacks for info, rows, and end-of-image.
