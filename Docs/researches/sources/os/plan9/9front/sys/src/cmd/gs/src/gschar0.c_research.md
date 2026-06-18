# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gschar0.c

## Role

`gschar0.c` implements Type 0/composite font string decoding for Ghostscript text enumeration.

This is font/text decoding infrastructure, not filesystem code.

## Main Functions

- `gs_type0_init_fstack(gs_text_enum_t *pte, gs_font *pfont)`
- `gs_type0_next_char_glyph(gs_text_enum_t *pte, gs_char *pchr, gs_glyph *pglyph)`

Internal helper:

- `gs_stack_modal_fonts(gs_text_enum_t *pte)`

## Font Stack Initialization

`gs_type0_init_fstack`:

- Requires text data to be string/bytes-backed.
- Initializes font stack depth to 0 with the supplied font.
- Calls `gs_stack_modal_fonts` to descend through modal composite fonts.

`gs_stack_modal_fonts`:

- Walks composite fonts while `FMapType` is modal.
- Selects descendants from `FDepVector` using `Encoding[0]`.
- Enforces `MAX_FONT_STACK`.

## Composite Decoding Behavior

`gs_type0_next_char_glyph` decodes the next character/glyph and returns:

- negative error on malformed data or invalid font
- `2` when the string is empty or exhausted
- `1` when the current base font changed
- `0` when the base font did not change

It handles:

- modal maps:
  - `fmap_escape`
  - `fmap_double_escape`
  - `fmap_shift`
- non-modal maps:
  - `fmap_8_8`
  - `fmap_1_7`
  - `fmap_9_7`
  - `fmap_SubsVector`
  - `fmap_CMap`

## Important Edge Cases

- Truncated multi-byte sequences return `gs_error_rangecheck`.
- Exceeding font stack depth returns `gs_error_invalidfont`.
- Initial escape or shift characters at string index 0 are handled specially from the root composite font, matching documented Adobe behavior discovered through compatibility testing.
- CMap decoding can return either a CID-like character or an explicit glyph. Undefined CMap glyphs become `gs_min_cid_glyph`.
- If an FMapType 4/5 decoding modifies the current character before a CMap descendant, the code builds a temporary modified buffer for `gs_cmap_decode_next`.
- For vertical metrics, CID base fonts may copy `FontBBox` into `pte->FontBBox_as_Metrics2`.

## Internal Macros

- `select_descendant(...)`: validates descendant index, updates stack depth/font/index, and marks changes.
- `need_left(n)`: validates remaining bytes.
- `subs_loop(...)`: helper for `SubsVector` decoding widths 1 to 4.

## Dependencies

Includes Ghostscript memory, font, CMap, fixed-point, device, and text internals.

## Notable Risks

- The function is dense and stateful: it mutates `pte->index`, `pte->fstack`, `pte->cmap_code`, and metrics fields.
- Several branches rely on `goto` labels for modal descent/ascent control flow.
- Correctness depends on composite font data structures being internally consistent: `Encoding`, `FDepVector`, `SubsVector`, `CMap`, and `FMapType`.
