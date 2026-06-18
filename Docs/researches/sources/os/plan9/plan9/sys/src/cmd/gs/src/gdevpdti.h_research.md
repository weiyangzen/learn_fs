# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdti.h

## Purpose
Defines the bitmap-font interface for `pdfwrite`.

## API Surface
- Page/text integration:
  - `pdf_close_text_page`
- Bitmap image character support:
  - `pdf_char_image_y_offset`
  - `pdf_begin_char_proc`
  - `pdf_end_char_proc`
  - `pdf_do_char_image`
- Internal bitmap-font lifecycle:
  - `pdf_bitmap_fonts_alloc`
  - `pdf_write_bitmap_fonts_Encoding`
  - `pdf_write_contents_bitmap`

## Integration
- Included by `gdevpdt.c`, `gdevpdt.h`, and bitmap/text implementation modules.
- Type 3 bitmap fonts are described as internally created fonts whose CharProc is a single bitmap image at device resolution.

## Risks and Notes
- The API is split between external bitmap image output used by `gdevpdfb.c` and internal font-writing helpers used by text code.
