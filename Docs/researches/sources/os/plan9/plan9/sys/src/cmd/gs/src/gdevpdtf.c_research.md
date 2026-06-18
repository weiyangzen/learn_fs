# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtf.c

## Purpose
Implements PDF font and CMap resource allocation/management, standard-font recognition, embedding decisions, BaseFont computation, resource array sizing, and CID width array allocation.

## Main Structures and GC
- Provides GC enumeration/relocation for `pdf_font_resource_t`, including BaseFont strings, descriptors, base fonts, Widths, used bitmaps, ToUnicode resources/CMaps, Type0 descendant fonts, CMap names, Type3 charprocs/resources, and CID arrays.
- Defines the 14 standard PDF font names and default base encodings.
- Allocates `pdf_outline_fonts_t` and its standard-font table.

## Main Functions
- `pdf_outline_fonts_alloc`, `pdf_standard_fonts`, and `pdf_clean_standard_fonts` manage standard font bookkeeping.
- `scan_for_standard_fonts` discovers standard fonts in the font directory.
- `find_std_appearance` compares a font’s outlines against known standard fonts.
- `font_resource_alloc`, `font_resource_simple_alloc`, and `font_resource_encoded_alloc` allocate generic, simple, and encoded font resource objects.
- `pdf_resize_resource_arrays` grows Widths/used/CIDToGID/vertical arrays for CID fonts whose documents use larger CIDs than expected.
- `pdf_font_resource_font` resolves copied font data through base font or descriptor.
- `pdf_font_embed_status` decides standard/no/yes embedding using PDF/X, compatibility level, NeverEmbed/AlwaysEmbed/EmbedAllFonts, symbolic status, and standard-font equivalence.
- `pdf_compute_BaseFont` computes final BaseFont names, handles Type0 CMap suffixes, MM Type1 spaces, TrueType space removal, subset prefixes, and descriptor FontName synchronization.
- Allocators create Type0, Type3, standard, simple, CIDFont, and CMap resources.
- `pdf_obtain_cidfont_widths_arrays` lazily allocates horizontal and vertical CID width/origin arrays.
- `pdf_cmap_alloc` delegates CMap writing.

## Integration
- Depends on base-font and descriptor APIs from `gdevpdtb.c` and `gdevpdtd.c`.
- Uses font writing callbacks declared in `gdevpdtw.h`.
- Called by text processing modules to obtain correct PDF font resources and arrays.

## Risks and Notes
- Standard-font substitution depends on font directory scanning, UniqueID checks, and glyph-outline compatibility.
- `pdf_resize_array` copies raw bytes and assumes caller passes correct element counts.
- CID vertical array allocation is deferred; text code must call `pdf_obtain_cidfont_widths_arrays` before writing vertical metrics.
- BaseFont finalization can invalidate copied-font UID for subset fonts to avoid writing inappropriate UIDs.
