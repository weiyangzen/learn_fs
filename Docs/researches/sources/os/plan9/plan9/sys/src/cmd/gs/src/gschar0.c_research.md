# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gschar0.c

Implements composite Type 0 font decoding for Ghostscript text enumeration.

Key contents:
- Includes memory, error, font map/CMap, fixed-point, device, font, Type 0 font, and text headers.
- Implements private `gs_stack_modal_fonts`.
- Implements public/internal composite helpers:
  - `gs_type0_init_fstack`
  - `gs_type0_next_char_glyph`
- Defines helper macro `select_descendant`.
- Defines private `root_esc_char`.

Behavior:
- `gs_type0_init_fstack` initializes the text enumerator font stack for byte-string text and stacks modal composite fonts down to a non-modal or base font.
- `gs_stack_modal_fonts` descends through modal composite fonts, using `Encoding[0]`, until it reaches a non-modal composite or base font.
- `gs_type0_next_char_glyph` decodes the next character/glyph from a composite string and returns:
  - error on malformed/incomplete sequences
  - `2` when the string is empty or exhausted
  - `1` when the base font changed
  - `0` otherwise
- Handles modal escape/shift font maps:
  - `fmap_escape`
  - `fmap_double_escape`
  - `fmap_shift`
- Handles non-modal descendant maps:
  - `fmap_8_8`
  - `fmap_1_7`
  - `fmap_9_7`
  - `fmap_SubsVector`
  - `fmap_CMap`
- For CMap descendants, calls `gs_cmap_decode_next`, preserves CMap code for widthshow behavior, and can return either character or glyph identity.
- Updates `pte->FontBBox_as_Metrics2` for CID encrypted and CID TrueType descendants where vertical metrics may use FontBBox.

Important implementation notes:
- The decoder has special handling for initial escape/shift bytes at the root of modal composite fonts, based on documented Adobe behavior confirmed by compatibility reports.
- Bounds checks use `need_left(n)` and return `gs_error_rangecheck` for truncated multibyte sequences.
- The implementation mutates the text enumerator’s font stack and string index as decoding proceeds.
- There is an explicit unresolved comment: descendant CMap rescanning after CMap decode is marked as a future/unfinished concern.
