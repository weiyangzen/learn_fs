# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdt.h

## Purpose
Narrow external interface for `pdfwrite` text and font handling. The file explicitly says it is the only text/font header that code outside `pdftext.dev` should include.

## API Surface
- Text state allocation and reset:
  - `pdf_text_state_alloc`
  - `pdf_text_data_alloc`
  - `pdf_reset_text_page`
  - `pdf_reset_text_state`
  - `pdf_close_text_page`
  - `pdf_close_text_document`
- Contents-state transitions:
  - `pdf_from_stream_to_text`
  - `pdf_from_string_to_text`
  - `pdf_close_text_contents`
- Bitmap font entry points for `gdevpdfb.c`:
  - `pdf_char_image_y_offset`
  - `pdf_begin_char_proc`
  - `pdf_end_char_proc`
  - `pdf_do_char_image`

## Integration
- Duplicates selected declarations from internal headers so the compiler can check consistency while hiding most internals from non-text modules.
- Depends on types declared elsewhere through `gdevpdfx.h` inclusion chains, especially `gx_device_pdf`, `pdf_text_data_t`, `pdf_char_proc_t`, and `pdf_stream_position_t`.

## Risks and Notes
- This header intentionally exposes only lifecycle, context transition, and bitmap-char APIs; other font-resource manipulation should remain inside the text subsystem.
- Mismatch between this facade and internal headers would create compile-time contract failures.
