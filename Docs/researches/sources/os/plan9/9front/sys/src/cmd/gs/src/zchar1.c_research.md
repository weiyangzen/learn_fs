# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar1.c

This file implements Type 1 character display and shared charstring execution support for Type 1, Type 2, Type 4/disk-based, and CID Type 0 flows.

Key behavior:
- `.type1execchar` delegates to `charstring_execchar` for Type 1 and disk-based fonts.
- Initializes a Type 1 interpreter using current gstate/path, text enumerator scale, alpha/oversampling rules, PaintType, and font data.
- Supports both valid-FontBBox and no-FontBBox execution paths:
  - bbox path sets cache before interpreting full outline when possible.
  - no-bbox path builds the outline first, derives bbox, sets cache, and may re-run for antialiasing oversampling.
- Handles Type 1 OtherSubrs by moving interpreter state to heap, pushing saved operands/continuations on the e-stack, and calling PostScript OtherSubrs.
- Implements fill/stroke finishing paths with compatibility adjustments for fill rule, StrokeWidth, and fill_adjust behavior.
- Exposes `.setweightvector` for Multiple Master Type 1/Type 2 weight vectors.
- Provides backend helpers:
  - Type 1 glyph data, subr data, SEAC data
  - stack push/pop callbacks for Type 1 interpreter
  - glyph outline construction
  - glyph info with Metrics, Metrics2, and CDevProc awareness
  - `z1_set_cache` for CID encrypted font cache setup

Important dependencies:
- Uses Type 1 interpreter structures from `gxtype1.h` and font structures from `gxfont1.h`.
- Depends on common char output helpers in `icharout.h` and show lifecycle helpers from `zchar.c`.

Research notes:
- This is one of the highest-risk files in the group because it bridges arbitrary PostScript execution, font charstring interpretation, stack manipulation, cache-device setup, and graphics-state restoration.
