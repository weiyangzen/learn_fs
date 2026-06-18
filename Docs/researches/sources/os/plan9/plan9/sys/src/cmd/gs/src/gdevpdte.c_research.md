# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdte.c

## Purpose
Implements encoding-based text processing for simple fonts: Type 1/2, TrueType/Type 42, and Type 3/user-defined fonts.

## Main Paths
- `pdf_encode_process_string` validates font type, obtains/updates a PDF font resource, then processes the encoded string.
- `pdf_add_ToUnicode` creates and populates ToUnicode CMaps for simple, CID0, and CID2 fonts.
- `pdf_register_charproc_resource` and `pdf_used_charproc_resources` track resources used inside Type 3 CharProcs.
- `pdf_encode_string` obtains a compatible PDF font resource, registers it, copies glyphs, populates encoding entries, marks used characters, and adds ToUnicode pairs.
- `process_text_estimate_bbox` estimates transformed text bounding boxes to skip text outside the clip box when Acrobat coordinate limits would be risky.
- `pdf_process_string` coordinates state update, fast-path text emission, width-return behavior, width modifications, clipping skip, and current-point updates.
- `pdf_char_widths` reads or computes cached Widths and real widths for a character.
- `process_text_return_width` computes total text width and detects when real widths differ from PDF Widths.
- `process_text_modify_width` emits text character-by-character when spacing, replaced widths, vertical origin shifts, or differing real/PDF widths require manual positioning.
- `pdf_encode_glyph` maps a glyph back to a one-byte character code when possible.
- `process_plain_text` adapts Ghostscript text input forms into byte strings and handles intervene/single-glyph cases.

## Integration
- Calls resource APIs from `gdevpdtt.c`, `gdevpdtf.c`, and `gdevpdtd.c`.
- Emits text through `gdevpdts.c` via `pdf_set_text_state_values` and `pdf_append_chars`.
- Uses Type 3 helpers from `gdevpdti.c` for charproc interactions.
- Supplies ToUnicode data used later by font-resource writing.

## Compatibility Behavior
- Avoids re-encoding text in modern paths to prevent encoding conflicts during font merging.
- Falls back for glyphshow if glyphs cannot be encoded with the current simple font.
- Handles Type 3 cached versus uncached charproc width behavior.
- Applies vertical writing and side-bearing shift handling through cached or computed `v` vectors.

## Risks and Notes
- Some fallback paths intentionally return errors so the default rendering path can produce outlines/bitmaps.
- Text enumerator state is temporarily mutated and restored in width-modification paths.
- `process_text_estimate_bbox` uses FontBBox per character, so it is conservative rather than exact.
- There is a likely typo in Type 3 vertical vector storage elsewhere consumed here (`v[ch].y` is assigned from `pcp->v.x` in `gdevpdti.c`).
