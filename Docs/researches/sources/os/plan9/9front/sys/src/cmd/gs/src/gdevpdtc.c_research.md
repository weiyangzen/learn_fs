# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtc.c

Composite and CID-keyed text processing for `pdfwrite`. It handles non-CMap composite fonts, CMap-based Type 0 fonts, CIDFont text, standard/embedded CMap selection, CID width tracking, CID-to-GID maps, and ToUnicode generation.

Key behavior:
- `process_composite_text` handles composite fonts with `FMapType != 9` by scanning text into runs that use the same leaf font, computing effective FontMatrix values, and delegating each run to simple-font encoding/text processing.
- Maintains current point and return-width accumulation when the caller requests width results.
- Rejects unsupported text sources and `TEXT_INTERVENE` cases for composite processing.
- Defines a table of standard PDF CMap names, with PDF 1.4-only names skipped for older compatibility levels.
- `attach_cmap_resource` uses a standard CMap name when possible, writes non-standard CMaps as resources, recognizes identity CMaps with non-standard names, and creates reusable identity ToUnicode CMaps for simple two-byte Unicode mappings.
- `scan_cmap_text` walks a Type 0 CMap text stream, resolves descendant CID fonts, obtains or creates CIDFont resources, resizes CID arrays when documents use CIDs beyond declared counts, records glyph usage, computes horizontal/vertical widths, fills CIDToGIDMap entries for CIDFontType2, and creates parent Type 0 font resources.
- Adds ToUnicode entries, including a workaround for PScript5-generated GlyphNames2Unicode data that uses character codes instead of CIDs.
- Handles `CDevProc` callout by stopping after the affected character and returning `TEXT_PROCESS_CDEVPROC`.
- Emits processed substrings through `process_text_modify_width`, preserving/restoring text parameters around width modification.
- `process_cmap_text` wraps `scan_cmap_text` and updates the text enum's CDevProc callout flag.
- `process_cid_text` supports CIDFont `glyphshow` by converting glyph numbers to two-byte Identity-CMap text, synthesizing a Type 0 font from the CIDFont when needed, and delegating to `process_cmap_text`.

Notable dependencies:
- Uses CMap/font internals from `gxfcmap.h`, `gxfont0.h`, `gxfont0c.h`, `gxfcid.h`, and text helpers from `gdevpdtt.h`.
- Calls font resource, descriptor, width, ToUnicode, and text-state helpers from `gdevpdtf.h`, `gdevpdtd.h`, `gdevpdte.c`, and `gdevpdts.h`.

Research notes:
- PDF has no direct `glyphshow` for CIDFont glyphs; the file represents it through a Type 0 font and Identity CMap.
- The code contains explicit compatibility notes for PScript5.dll and Windows-generated CMaps.
- Width and resource updates happen while scanning, before actual text emission, so the final PDF font dictionaries can be written correctly at document close.
- This is text/font output logic, not filesystem functionality.
