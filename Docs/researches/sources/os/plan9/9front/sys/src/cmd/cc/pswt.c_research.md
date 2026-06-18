# File Research: sources/os/plan9/9front/sys/src/cmd/cc/pswt.c

Portable switch lowering helpers, long-string output, unused-result warning helper, and IEEE double conversion.

Key behavior:
- `doswit` collects `case` entries, detects duplicate cases/defaults, sorts case values, and delegates normal switch generation to `swit1`.
- Handles 64-bit switch constants on 32-bit targets by switching first on high words and then on low words.
- `casf` allocates and links a new `Case`.
- `outlstring` emits wide string data respecting target byte order/alignment.
- `nullwarn` emits “result of operation not used” and still generates operand side effects.
- `ieeedtod` converts a native double into the compiler’s `Ieee` high/low representation.

Dependencies:
- Includes `gc.h`.
- Depends on back-end `swit1`, branch patching, string emission, and target alignment helpers.

Research notes:
- The switch code preserves signed-vs-unsigned behavior by tracking whether the expression/cases require vlong handling.
