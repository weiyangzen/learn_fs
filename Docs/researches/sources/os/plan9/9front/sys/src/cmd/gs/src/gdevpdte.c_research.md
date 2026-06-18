# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdte.c

Encoding-based Type 1/Type 2/Type 42/simple-font text processing for `pdfwrite`. It obtains encoded font resources, records glyph/encoding/ToUnicode data, estimates text bounds, emits high-level PDF text when possible, and falls back to per-character positioning when widths differ.

Key behavior:
- `pdf_encode_process_string` accepts simple Ghostscript font types (`ft_TrueType`, `ft_encrypted`, `ft_encrypted2`, `ft_user_defined`), encodes or records the string, and sends it to the processing path.
- `pdf_add_ToUnicode` lazily creates a ToUnicode CMap for a font resource and records character-code to Unicode mappings when glyph decoding succeeds.
- Tracks resources used inside Type 3 charprocs and marks nested font/resources as used when a Type 3 font is emitted.
- `pdf_encode_string` obtains a compatible PDF font resource, registers it in substream resources, copies glyphs into base fonts/descriptors, records encoding entries and Differences, adds encodings to copied fonts, handles incomplete "complete" font copies, records used characters, and always builds ToUnicode data for simple fonts.
- `process_text_estimate_bbox` estimates a string's device-space bounding box using the font bbox and current text matrix so text outside the clip can be skipped to avoid huge-coordinate Acrobat problems.
- `pdf_process_string` updates text state, chooses fast `Tj`/`TJ` emission when widths match, or delegates to `process_text_modify_width` when PostScript width operations or real-width differences need explicit positioning.
- Supports `TEXT_RETURN_WIDTH`, `TEXT_DO_DRAW`, `TEXT_DO_NONE`, `TEXT_ADD_TO_ALL_WIDTHS`, `TEXT_ADD_TO_SPACE_WIDTH`, and `TEXT_REPLACE_WIDTHS`.
- `pdf_char_widths` computes/caches PDF Widths and real widths, including Type 3 width arrays and vertical-writing origin adjustments.
- `process_text_return_width` computes total width and detects whether cached real widths differ from PDF Widths.
- `process_text_modify_width` emits characters one at a time, handles glyph-origin shifts, character/word spacing, replacement widths, vertical writing, composite text, CDevProc results, and text matrix repositioning between characters.
- `pdf_encode_glyph` maps a glyph back to a single-byte character code by scanning the font encoding.
- `process_plain_text` converts different Ghostscript text sources into byte strings: strings/bytes, chars, single chars, glyph arrays, and single glyphs. If glyph encoding fails, it tries an unencoded font resource path before allowing fallback.

Notable dependencies:
- Uses Ghostscript font, path, text, and CMap APIs from `gxfont*.h`, `gxfcmap.h`, `gxfcopy.h`, and `gxpath.h`.
- Uses font-resource and descriptor APIs from `gdevpdtf.h`, `gdevpdtd.h`, and shared text helpers from `gdevpdtt.h` and `gdevpdts.h`.
- Uses graphics/resource helpers from `gdevpdfg.h` and `gdevpdfx.h`.

Research notes:
- The file intentionally avoids re-encoding text in newer behavior because font merging can cause encoding conflicts.
- It contains several viewer compatibility guards around huge coordinates, Type 3 widths, vertical glyph origins, and Acrobat text-position limitations.
- `RIGHT_SBW` selects the current sidebearing/origin-shift logic, leaving the older helper compiled out.
- This is text output logic, not filesystem functionality.
