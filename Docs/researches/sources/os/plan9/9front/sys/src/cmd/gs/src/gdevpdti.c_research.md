# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdti.c

Bitmap and Type 3 CharProc implementation for `pdfwrite`. It creates synthesized bitmap fonts, accumulates Type 3 charprocs, manages substream save/restore, deduplicates charprocs, writes Type 3 font contents, and registers substream resources.

Key behavior:
- Defines `pdf_char_proc_t` pseudo-resources with owning font, next pointer, Y offset, character code/name, real width, and vertical origin.
- Defines `pdf_bitmap_fonts_t` with current open synthesized Type 3 font, reuse flag, shared bitmap Encoding object ID, and maximum embedded character code.
- `assign_char_code` creates/reuses synthesized Type 3 bitmap fonts, increments synthetic font names (`A`, `B`, ...), assigns character codes, stores rounded widths, and creates ToUnicode mappings through the current text enum.
- `pdf_write_contents_bitmap` writes Type 3 font dictionaries: Encoding reference, CharProcs dictionary, FontMatrix, and Type 3 finishing data. For non-bitmap Type 3 fonts it writes an explicit Encoding object.
- `pdf_bitmap_fonts_alloc` initializes bitmap-font bookkeeping.
- `pdf_close_text_page` prevents adding new chars to a Type 3 font across pages for PDF 1.2/Acrobat Reader 3 compatibility.
- `pdf_char_image_y_offset` computes a plausible vertical offset for bitmap character images relative to current text position.
- `pdf_begin_char_proc` and `pdf_end_char_proc` create encrypted CharProc stream objects, reserve/fill stream length in place, and update bitmap Type 3 FontBBox/max offset data.
- `pdf_do_char_image` emits a bitmap character as text using the synthesized Type 3 font and image placement matrix.
- `pdf_write_bitmap_fonts_Encoding` writes the shared synthetic bitmap Encoding Differences object.
- `pdf_start_charproc_accum` enters substream accumulation mode for a Type 3 charproc resource.
- `pdf_set_charproc_attrs` installs charproc metadata, writes `d0`/`d1` width/bbox operators, toggles color skipping per Type 3 cache behavior, marks used/cached bits, and records the active Type 3 owner.
- `pdf_open_aside` and `pdf_close_aside` open and close stream COS objects in temporary aside storage, attaching compression filters without immediate final document output.
- `pdf_enter_substream` saves current stream, context, text state, clip path, viewer graphics state, procsets, resources, Type 3 owner, soft-mask state, object name, and related flags before accumulating a nested object.
- `pdf_exit_substream` restores all saved context and viewer/text state after closing the accumulated stream.
- CharProc deduplication compares character code, encoding/glyph, name, real width, vertical origin, bitmap flag, FontMatrix, encoding compatibility, and COS stream content equality.
- `pdf_end_charproc_accum` exits accumulation, deduplicates or installs the charproc, handles glyph variations by creating another Type 3 font when needed, updates widths/real widths/used bits, and propagates widths for all encoding slots that map to the same glyph.
- `pdf_add_procsets` writes `/ProcSet` arrays.
- `pdf_add_resource` adds a resource reference to a substream resource dictionary and marks resources global for ps2write global-object accumulation when needed.

Notable dependencies:
- Uses text state and font-resource APIs from `gdevpdts.h`, `gdevpdtf.h`, `gdevpdtw.h`, and `gdevpdtt.h`.
- Uses graphics state save/restore and COS object helpers from `gdevpdfg.h`, `gdevpdfx.h`, and `gdevpdfo.h`.

Research notes:
- The file does more than bitmap fonts: it is also the generic substream/charproc accumulation machinery used by Type 3 and other nested PDF resources.
- The in-place CharProc length update assumes length fits in six digits; longer streams return `limitcheck`.
- Comments document Acrobat Reader 3 bugs around Type 3 Encoding and cross-page font downloading.
- This is PDF font/substream infrastructure, not filesystem code.
