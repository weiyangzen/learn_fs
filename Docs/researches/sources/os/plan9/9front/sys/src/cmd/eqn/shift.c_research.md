# File Research: sources/os/plan9/9front/sys/src/cmd/eqn/shift.c

This file implements subscripts and superscripts.

Key responsibilities:
- `subsup` dispatches to single sub/sup handling or combined sub+sup handling.
- `bshiftb` attaches one subscript or superscript to a base box.
- `shift2` attaches both subscript and superscript, measuring their widths and aligning them as a pair.
- Updates height, baseline, font, and character class metadata after shifts.
- Emits point-size transitions for smaller sub/sup text.

Important implementation notes:
- Spacing depends on italic/roman state and character classes.
- Tuning globals include `Subbase`, `Supshift`, `Sub1space`, `Sup1space`, `Sub2space`, `SS1space`, and `SS2space`.
- Combined sub/sup uses a temporary width register and frees both attached boxes.
