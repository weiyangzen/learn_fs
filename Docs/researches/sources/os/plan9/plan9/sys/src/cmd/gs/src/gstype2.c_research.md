# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype2.c

Purpose: Implements the Adobe Type 2 charstring interpreter for Ghostscript Type 1/CFF font execution.

Key entry point:
- `gs_type2_interpret(gs_type1_state *pcis, const gs_glyph_data_t *pgd, int *ignore_pindex)` continues or starts Type 2 charstring execution, returns normal completion, errors, or positive intervention codes.

Important internals:
- `type2_sbw()` handles initial side-bearing/width setup, including nominal/default CFF width logic and backing up the interpreter pointer so the current operator re-executes.
- `type2_vstem()` parses vertical stem hint operands and updates `pcis->num_hints`.
- `check_first_operator()` detects the first real operator and delegates width setup before continuing interpretation.

Behavior:
- Decodes Type 2 operand encodings, subroutine calls, global subroutines, masks, arithmetic/stack extended operators, moves, lines, curves, flex operators, blend, and `endchar`.
- Uses the Type 1 hinter API (`t1_hinter__*`) as the output consumer for outlines and hints.
- Handles Type 2 `endchar` with 4 or 5 operands as Type 1-style `seac` accented glyph composition.
- Parses `hintmask`/`cntrmask` bytes based on accumulated hint count; `cntrmask` is explicitly parsed but not implemented.

Dependencies:
- Depends on `gxfont1.h`, `gxtype1.h`, `gxhintn.h`, fixed arithmetic, current transformation state, and Ghostscript charstring decrypt/decode macros.

Notable risks:
- `random` and counter masks are marked not implemented.
- Registry support is faked as a single registry backed by `WeightVector`.
- Some invalid subroutine calls are intentionally ignored for Acrobat compatibility.
