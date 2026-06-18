# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtw.c

## Role

`gdevpdtw.c` writes pdfwrite font and CMap resources. It serializes simple fonts, Type 0 fonts, Type 3 fonts, CIDFonts, Encodings, ToUnicode resources, CIDSystemInfo dictionaries, and CMaps.

## Font Writing

- `pdf_write_Widths()` writes `/FirstChar`, `/LastChar`, and `/Widths`.
- `pdf_write_encoding()`, `pdf_write_encoding_ref()`, and `pdf_different_encoding_index()` build Encoding objects and Differences arrays.
- `pdf_write_contents_type0()`, `pdf_finish_write_contents_type3()`, `pdf_write_contents_std()`, `pdf_write_contents_simple()`, `pdf_write_contents_cid0()`, and `pdf_write_contents_cid2()` implement per-font-type resource content writers.
- `pdf_write_contents_cid2()` emits a compressed `/CIDToGIDMap` stream only when the map is non-identity.
- `pdf_write_font_resource()` writes common font dictionary keys: `/BaseFont`, `/FontDescriptor`, `/ToUnicode`, `/Type`, and OPDF `.Global`.

## Width And ToUnicode Decisions

- `pdf_compute_CIDFont_default_widths()` builds a width histogram to choose default CID widths and vertical metrics.
- `pdf_write_CIDFont_widths()` writes `/DW`, `/W`, `/DW2`, and `/W2`, skipping undefined copied-font glyphs but preserving used zero widths.
- `pdf_simple_font_needs_ToUnicode()` uses encoding entries and `gs_c_pdf_glyph_type[]` to determine whether a simple font can safely omit ToUnicode.

## Document Close Flow

`pdf_close_text_document()` cleans standard fonts, drops the font cache, writes charprocs, finishes embedded font descriptors, writes CIDFont and Font resources, writes descriptors, then writes bitmap-font Encoding resources.

## CMap Writing

- `pdf_write_cid_system_info()` writes Registry/Ordering/Supplement, encrypting strings if required.
- `pdf_write_cmap()` creates a data stream, fills CMap dictionary metadata for non-ToUnicode maps, writes the CMap with `psf_write_cmap()`, and ends the stream.

## Dependencies

This file depends on Ghostscript font/CMap APIs, PostScript font writer helpers, PDF object/resource/data-stream code, font descriptor code, bitmap font code, generated glyph attributes from `gdevpdtv.h`, and ARC4 encryption support.

## Risks And Invariants

- Encoding Difference generation must match the selected BaseEncoding and Type 3 compatibility behavior.
- ToUnicode omission depends on the generated glyph table and glyph-name normalization; mistakes affect text extraction/search.
- CID width emission assumes used-glyph bitmaps and width arrays are aligned by CID.
- CMap streams are deliberately not encrypted during temporary-file writing; encryption is handled through the surrounding PDF data path.
