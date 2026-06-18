# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngpread.c

## Purpose

`pngpread.c` implements libpng's progressive, push-mode PNG reader. Instead of reading from a blocking stream in one call sequence, the application feeds arbitrary input buffers to libpng with `png_process_data()`, and libpng resumes parsing from its saved state.

This is vendored libpng reader infrastructure inside the Plan 9 Ghostscript source tree.

## Main Responsibilities

- Maintain a push-mode parse state machine.
- Validate the PNG signature incrementally.
- Parse chunk headers only when enough bytes are available.
- Dispatch known PNG chunks to the same handlers used by the sequential reader.
- Buffer incomplete input across application calls.
- Stream IDAT data through zlib and emit rows through callbacks.
- Support progressive callbacks for info, row, and end events.
- Handle progressive text chunks (`tEXt`, `zTXt`, `iTXt`) and unknown chunks.

## State Machine

The file defines push-mode process states:

- `PNG_READ_SIG_MODE`
- `PNG_READ_CHUNK_MODE`
- `PNG_READ_IDAT_MODE`
- `PNG_SKIP_MODE`
- `PNG_READ_tEXt_MODE`
- `PNG_READ_zTXt_MODE`
- `PNG_READ_iTXt_MODE`
- `PNG_READ_DONE_MODE`
- `PNG_ERROR_MODE`

`png_process_data()` restores the current input buffer and repeatedly calls `png_process_some_data()` until no buffered bytes remain.

`png_process_some_data()` dispatches based on `png_ptr->process_mode`.

## Signature and Chunk Parsing

`png_push_read_sig()` accumulates the 8-byte PNG signature in `info_ptr->signature`, comparing only the newly available bytes. It distinguishes non-PNG input from likely ASCII-converted PNG corruption.

`png_push_read_chunk()` reads chunk length and type once at least 8 bytes are available, then dispatches:

- Core chunks: `IHDR`, `PLTE`, `IDAT`, `IEND`
- Ancillary chunks: `gAMA`, `sBIT`, `cHRM`, `sRGB`, `iCCP`, `sPLT`, `tRNS`, `bKGD`, `hIST`, `pHYs`, `oFFs`, `pCAL`, `sCAL`, `tIME`
- Text chunks: `tEXt`, `zTXt`, `iTXt`
- Unknown chunks via `png_push_handle_unknown()`

Before handling most chunks, it checks that chunk payload plus CRC are already buffered; otherwise it saves the buffer and returns.

## IDAT Processing

When `IDAT` is encountered:

- The reader verifies `IHDR` exists.
- Palette images must already have `PLTE`.
- `png_ptr->idat_size` is set from the chunk length.
- `png_ptr->process_mode` switches to `PNG_READ_IDAT_MODE`.
- `png_push_have_info()` invokes the application info callback.
- zlib output is set to the row buffer.

`png_push_read_IDAT()` then consumes IDAT payload from either the saved buffer or the current buffer, updates CRC, and feeds bytes to `png_process_IDAT_data()`.

`png_process_IDAT_data()` inflates with `Z_PARTIAL_FLUSH`, emits complete rows when `avail_out` reaches zero, detects extra compressed data, marks zlib completion, and reports decompression errors.

## Buffer Management

Progressive reading is built around three buffer fields:

- Saved bytes from previous incomplete calls.
- Current application-supplied bytes.
- Combined logical `buffer_size`.

Important helpers:

- `png_push_fill_buffer()` copies requested bytes from saved data first, then current data.
- `png_push_save_buffer()` compacts or grows `save_buffer` and appends any unconsumed current bytes.
- `png_push_restore_buffer()` installs the newest caller-provided buffer.

The save-buffer growth path checks for potential overflow before adding `current_buffer_size + 256`.

## Row Emission and Interlace Handling

`png_push_process_row()` builds `row_info`, applies PNG row filters, copies the row to `prev_row`, applies read transformations, and emits rows through `png_push_have_row()`.

For interlaced images with `PNG_INTERLACE` transformation enabled, the code expands sparse Adam7 pass rows into full display rows and emits `NULL` rows for generated/skipped display positions. `png_read_push_finish_row()` advances row/pass state and recomputes interlace pass width, row byte counts, and number of rows.

## Progressive Text Handling

Text chunks are handled as multi-step progressive modes:

- `png_push_handle_tEXt()` allocates `current_text`, then `png_push_read_tEXt()` fills it across input calls, validates CRC, splits key/text, and calls `png_set_text_2()`.
- `png_push_handle_zTXt()` and `png_push_read_zTXt()` read compressed text, validate compression marker, inflate into a dynamically grown buffer, and then store text metadata.
- `png_push_handle_iTXt()` and `png_push_read_iTXt()` parse international text fields: keyword, compression flag/type, language, translated keyword, and text.

For `PNG_MAX_MALLOC_64K`, large text chunks are either truncated/skipped or rejected depending on chunk type.

## Unknown Chunk Handling

`png_push_handle_unknown()` validates the chunk name, errors on unhandled unknown critical chunks, optionally stores unknown chunks when configured, invokes user unknown-chunk callbacks, then skips remaining bytes through `png_push_crc_skip()`.

`png_push_crc_finish()` consumes skipped data while updating CRC and returns to chunk mode after CRC validation.

## Callback API

- `png_set_progressive_read_fn()` sets `info_fn`, `row_fn`, and `end_fn`, then routes read I/O through `png_push_fill_buffer`.
- `png_get_progressive_ptr()` returns `png_ptr->io_ptr`.
- `png_progressive_combine_row()` combines an incoming interlace row into an old row using the pass display mask.

## Research Notes

The file mirrors much of the sequential reader logic but adds explicit resumability. The core invariant is that chunk handlers are called only after the complete chunk body plus CRC is present, except IDAT and progressive text modes, which have dedicated incremental paths.
