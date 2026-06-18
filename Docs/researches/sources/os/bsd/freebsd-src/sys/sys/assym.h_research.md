# File Research: sources/os/bsd/freebsd-src/sys/sys/assym.h

Assembly symbol/offset generation macros.

Key elements:
- Defines `ASSYM_BIAS`, `ASSYM_ABS`, and `ASSYM()` to encode numeric values into array sizes.
- Defines `OFFSYM()` to emit offset-sized symbols and assert member type compatibility.
- Optional `OFFSET_TEST` enables layout offset assertions against `_lite` structures.

Dependencies:
- Requires `offsetof`, `CTASSERT`, and compiler type builtins from context.

Research notes:
- Used to generate constants consumed by assembly code.
- Helps keep assembly offsets synchronized with C structure layouts.
