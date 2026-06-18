# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor3.c

This file implements the Level 3 internal UseCIEColor setter.

Key behavior:
- `.setuseciecolor` stores the supplied boolean-like ref into `istate->use_cie_color`.
- The comment states this parameter mirrors the `UseCIEColor` page-device parameter and may be set only in language level 3.
- Operand checking is intentionally omitted because the operator is only accessible during controlled initialization paths.

Important dependencies:
- Uses interpreter graphics state from `igstate.h`.
- Registered in `zcolor3_l3_op_defs`.

Research notes:
- This is a tiny state-setting companion to `.getuseciecolor` in `zcolor.c`.
