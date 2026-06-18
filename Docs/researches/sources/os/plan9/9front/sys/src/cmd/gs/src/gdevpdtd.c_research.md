# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtd.c

FontDescriptor implementation for `pdfwrite`. It computes PDF font descriptor metrics, owns the descriptor-to-base-font relationship, writes embedded-font references and descriptor dictionaries, and handles subset-specific CharSet/CIDSet entries.

Key behavior:
- Defines common descriptor values: required metrics (`Ascent`, `CapHeight`, `Descent`, `ItalicAngle`, `StemV`, `FontBBox`, `FontName`, `Flags`) and optional metrics (`AvgWidth`, `Leading`, `MaxWidth`, `MissingWidth`, `StemH`, `XHeight`).
- Defines `pdf_font_descriptor_t` for actual fonts and `pdf_sub_font_descriptor_t` for CID FD dictionary character-class entries.
- Allocates descriptors as pseudo-resources and creates a `pdf_base_font_t` at the same time.
- Exposes descriptor ID, font type, embedding status, subset status, descriptor/base names, copied font access, complete-copy dropping, and glyph-use recording.
- `pdf_compute_font_descriptor` scans the font glyph space to compute bounding boxes, ascent/descent, missing width, fixed-width status, cap height, x-height, italic angle, StemV, and flags.
- Applies 1000-unit scaling for TrueType/CID TrueType metrics and handles CID fonts with existing FontBBox specially.
- Uses glyph-name heuristics for Roman fonts to infer capitals, lowercase dimensions, serif/script/italic/small-caps-like flags, and stem width.
- `pdf_finish_FontDescriptor` computes metrics and writes the embedded font before the descriptor dictionary is written.
- `pdf_write_FontDescriptor` writes the descriptor dictionary, CIDSet for CID subsets, CharSet for Type 1 subsets, FontFile entries for embedded fonts, optional CID style/language/FD data, and then writes the referenced FontFile object.
- Marks embedded subset TrueType fonts symbolic as an Acrobat compatibility workaround.
- `pdf_release_FontDescriptor_components` frees the associated base font and is explicitly underimplemented.

Notable dependencies:
- Uses `gdevpdtb.c` for base-font copying, subset decisions, FontFile writing, CharSet, and CIDSet.
- Uses `gdevpdfo.h` for COS object state and writing.
- Uses Ghostscript glyph metrics, font flags, rectangle handling, and math helpers.

Research notes:
- Comments explain the one-to-one relationship used here between BaseFonts and FontDescriptors, even though PDF permits more.
- The file preserves old Acrobat interpretations of the `Flags` bit shared by StandardEncoding/Adobe Roman.
- There appears to be a likely typo in the CID FontBBox fast path: `desc.FontBBox.p.x` is assigned twice, and `p.y` is not assigned there.
- This is PDF font metadata generation, not filesystem code.
