# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ttcalc.h

Purpose: arithmetic API and type setup for TrueType calculations.

Key contents:
- Defines `Int16`, `Word16`, `Int32`, and `Word32` from configured integer sizes.
- Detects native 64-bit support through `long`, GCC `long long`, or MSVC `__int64`.
- In native mode defines `Int64` plus fast macros for multiply/divide, add, subtract, multiply, divide, and square roots.
- In fallback mode defines struct-based `Int64` and declares helper functions.
- Provides fixed-point conversion macros such as `MUL_FIXED`, `INT_TO_F26DOT6`, `INT_TO_FIXED`, `F2DOT14_TO_FIXED`, `FLOAT_TO_FIXED`, and `ROUND_F26DOT6`.

Dependencies: `ttcommon.h`, `tttypes.h`, and size macros from TrueType config.

Integration notes: shared between TrueType parsing and outline code.

Risks: relies on `SIZEOF_INT`/`SIZEOF_LONG` being correctly defined by `ttconf.h`.
