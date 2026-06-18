# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/jis.h

This header contains macro utilities for Japanese character-set conversion between JIS X 0208 coordinate bytes and Microsoft Shift-JIS byte pairs.

Key contents:
- `J2S(_h, _l)` transforms valid JIS X 0208 high/low bytes into Shift-JIS bytes.
- `S2J(_h, _l)` transforms valid Shift-JIS high/low bytes back into JIS X 0208 bytes.
- `ISJKANA(_b)` identifies JIS X 0201 halfwidth katakana bytes in `0xA0..0xDF`.
- `CANS2JH(_h)`, `CANS2JL(_l)`, and `CANS2J(_h, _l)` validate Shift-JIS lead/trail bytes usable for conversion.
- `CANJ2SB(_b)` and `CANJ2S(_h, _l)` validate JIS X 0208 graphic-set bytes in `0x21..0x7E`.

Important details:
- The conversion macros mutate their arguments in place; callers must pass modifiable byte variables, not expressions with side effects.
- The macros encode the Shift-JIS discontinuities around `0x7F` and `0xA0..0xDF`.
- `CANS2JH` excludes halfwidth-katakana bytes even though they are in the wider high-byte area.
- The comments document intended preconditions: `J2S` and `S2J` expect already validated input ranges.
- The macro style uses comma expressions and multi-statement blocks, matching old Plan 9 C conventions.

Filesystem relevance:
- Indirect: supports Japanese text conversion for file and stream contents handled by `tcs`.
