# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ttcalc.h

Header for TrueType arithmetic computations.

Key points:
- Includes `ttcommon.h` and `tttypes.h`.
- Defines exact 16-bit and 32-bit integer aliases from `SIZEOF_INT`/`SIZEOF_LONG`.
- Detects native 64-bit support through 8-byte `long`, optional GCC `long long`, or MSVC `__int64`.
- In `LONG64` mode, maps 64-bit operations to native expressions.
- Otherwise defines `Int64` as `{ lo, hi }` and maps macros to helper functions.
- Declares multiplication/division, 64-bit add/sub/mul/div/order/sqrt helpers as appropriate.
- Defines fixed-point conversion macros:
  - `MUL_FIXED`
  - `INT_TO_F26DOT6`
  - `INT_TO_F2DOT14`
  - `INT_TO_FIXED`
  - `F2DOT14_TO_FIXED`
  - `FLOAT_TO_FIXED`
  - `ROUND_F26DOT6`

Dependencies and interactions:
- Used by `ttfmain.c` and FreeType-derived TrueType internals.

Research relevance:
- Public arithmetic interface for TrueType fixed-point math.
