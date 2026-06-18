# File Research: sources/os/plan9/9front/sys/src/cmd/dict/kuten.h

Japanese/Chinese double-byte conversion macros and table declarations.

Key elements:
- Defines `J2S` for JIS X 0208 to Shift-JIS conversion.
- Defines `S2J` for Shift-JIS to JIS X 0208 conversion.
- Provides validity macros for Shift-JIS and JIS byte ranges.
- Declares table sizes: `JIS208MAX`, `GB2312MAX`, `BIG5MAX`.
- Externs `tabjis208`, `tabgb2312`, and `tabbig5`.

Dependencies:
- Used by `world.c`, `jis208.c`, and `gb2312.c`.

Research notes:
- `tabbig5` is declared here but not part of this grouped file set.
- Macros mutate their byte arguments in place.
