# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/kuten.h

This header defines Japanese/Chinese character-set conversion helpers and table sizes.

Key contents:
- `J2S(_h, _l)` converts JIS X 0208 high/low bytes to Microsoft Shift-JIS bytes.
- `S2J(_h, _l)` converts Microsoft Shift-JIS bytes back to JIS X 0208 high/low bytes.
- `ISJKANA()` recognizes JIS X 0201 katakana byte range.
- `CANS2JH()`, `CANS2JL()`, and `CANS2J()` validate Shift-JIS byte pairs.
- `CANJ2SB()` and `CANJ2S()` validate JIS graphic bytes/pairs.
- Defines table sizes `JIS208MAX`, `GB2312MAX`, and `BIG5MAX`.
- Declares external rune tables `tabjis208`, `tabgb2312`, and `tabbig5`.

Notable implementation details:
- Conversion is implemented as macros that mutate caller-provided high/low byte variables.
- The comments attribute the Shift-JIS “goo” to Kogure.
