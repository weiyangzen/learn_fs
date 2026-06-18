# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/sqrt.c

This file renders square roots.

Key responsibilities:
- Estimates a radical point size from the operand height and current point size.
- Adjusts output height based on device type.
- Measures operand width.
- Emits a radical glyph and overbar rule around the operand.
- Preserves the operand register as the result.
- Marks left/right font metadata as roman.

Important implementation notes:
- PostScript uses a different radical scale than CAT/APS/202 devices.
- The code uses register `10` for computed radical size and sets `.af 10 01` once to make it print as two digits.
- Comments acknowledge square-root rendering is approximate and device-specific.
