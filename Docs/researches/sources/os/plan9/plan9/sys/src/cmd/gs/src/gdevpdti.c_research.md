# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdti.c

## Purpose
Implements bitmap-font and Type 3 CharProc support for `pdfwrite`, including synthesized bitmap fonts, vector Type 3 charproc accumulation, substream save/restore, duplicate CharProc detection, and substream resource dictionaries.

## Main Structures
- `pdf_char_proc_t` is a pseudo-resource with owning font, same-font chain link, y offset, char code/name, real width, and vertical origin vector.
- `pdf_bitmap_fonts_t` tracks the current synthesized Type 3 bitmap font, encoding object ID, and max embedded code.

## Main Functions
- `assign_char_code` creates/reuses synthesized Type 3 bitmap fonts, assigns character codes, stores widths, and creates ToUnicode mappings.
- `pdf_write_contents_bitmap` writes Type 3 `/Encoding`, `/CharProcs`, `/FontMatrix`, and delegates common Type 3 finalization.
- `pdf_bitmap_fonts_alloc` initializes bitmap-font state.
- `pdf_close_text_page` prevents adding characters to existing Type 3 fonts across pages for old Acrobat compatibility.
- `pdf_char_image_y_offset` computes bitmap character y-offset relative to current text position.
- `pdf_begin_char_proc` and `pdf_end_char_proc` open/write/close bitmap CharProc streams with inline length patching and encryption support.
- `pdf_do_char_image` emits a bitmap image reference as text using the synthesized Type 3 font.
- `pdf_write_bitmap_fonts_Encoding` writes the shared bitmap encoding differences object.
- `pdf_start_charproc_accum`, `pdf_set_charproc_attrs`, and `pdf_end_charproc_accum` manage Type 3 vector charproc capture, widths, cache flags, duplicate detection, and font attachment.
- `pdf_open_aside`/`pdf_close_aside` create Cos stream objects in temporary storage.
- `pdf_enter_substream`/`pdf_exit_substream` save and restore device state around nested substream accumulation.
- `pdf_add_procsets` and `pdf_add_resource` populate substream Resources dictionaries.

## Integration
- Uses font resource allocation from `gdevpdtf.c`, text-state APIs from `gdevpdts.c`, and resource/object APIs from `gdevpdfx.h`.
- Interacts with viewer graphics state save/restore and graphics reset helpers outside this group.
- Registers resources used inside Type 3 charprocs so page/substream resource dictionaries remain complete.

## Risks and Notes
- CharProc length is patched into a fixed-width placeholder and rejects streams longer than 999999 bytes.
- Substream state save/restore touches many `gx_device_pdf` fields; missing one can corrupt nested charprocs/patterns/masks.
- Duplicate CharProc detection uses Cos object equality and encoding compatibility.
- In `pdf_end_charproc_accum`, `pdfont->u.simple.v[ch].y` is assigned `pcp->v.x`, likely a typo for `pcp->v.y`.
