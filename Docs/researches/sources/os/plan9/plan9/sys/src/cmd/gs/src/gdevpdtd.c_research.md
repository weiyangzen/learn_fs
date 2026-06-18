# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtd.c

## Purpose
Implements `pdf_font_descriptor_t`, the pseudo-resource layer for PDF FontDescriptor objects and descriptor metric computation.

## Main Structures
- `pdf_font_descriptor_values_t` stores required and optional FontDescriptor metrics: Ascent, CapHeight, Descent, ItalicAngle, StemV, FontBBox, FontName, Flags, AvgWidth, Leading, MaxWidth, MissingWidth, StemH, XHeight.
- `pdf_font_descriptor_common_t` embeds `pdf_resource_common` plus descriptor values.
- `pdf_font_descriptor_t` adds base font, font type, embedding flag, and CID-specific Style/Lang/FD values.
- `pdf_sub_font_descriptor_t` models FD dictionary entries for CID-keyed character classes.

## Main Functions
- `pdf_font_descriptor_alloc` allocates a descriptor pseudo-resource and associated base font.
- Accessors expose object ID, font type, embedding state, subset state, names, and copied font.
- `pdf_font_used_glyph` forwards glyph copying to the base font.
- `pdf_compute_font_descriptor` scans glyphs to compute metrics and flags, including symbolic/roman/fixed-width/italic/serif/small-caps heuristics.
- `pdf_finish_FontDescriptor` computes descriptor metrics and writes embedded font data if required.
- `pdf_write_FontDescriptor` writes the PDF FontDescriptor dictionary, including CIDSet, CharSet, FontFile, Style, Lang, and FD entries.
- `pdf_release_FontDescriptor_components` frees the base font pointer but is marked underimplemented.

## Integration
- Depends on `gdevpdtb.c` for base-font storage and embedded font output.
- Used by font resources in `gdevpdtf.c` and writing code in `gdevpdtw.c`.
- Writes Cos objects through `pdf_open_separate`, `COS_WRITE`, and `COS_WRITE_OBJECT`.

## Risks and Notes
- Descriptor metric computation is heuristic and explicitly described as crude in places.
- Contains compatibility hack marking embedded subset TrueType fonts symbolic for Acrobat behavior.
- There appears to be a duplicated assignment to `desc.FontBBox.p.x` when initializing CID FontBBox from base font values; likely intended to set both p/q x values.
- Error handling during glyph metric scans skips many non-VM errors because this can run indirectly during finalization.
