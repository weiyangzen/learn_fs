# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstype1.c

## Purpose
Implements the Adobe Type 1 charstring interpreter. It decodes encrypted or plain Type 1 charstrings, handles subroutines and escape operators, delegates hint/path operations to the Type 1 hinter, and returns positive intervention codes for caller-managed behavior such as side-bearing width and unknown OtherSubrs.

## Public Surface
- `gs_type1_interpret(gs_type1_state *pcis, const gs_glyph_data_t *pgd, int *pindex)`: continue interpreting a Type 1 charstring. Returns 0 for completion, negative Ghostscript errors, or positive Type 1 result codes.

## Initialization and State
- Uses `pcis->init_done` to initialize the hinter and finish Type 1 state setup on first/continued calls.
- Sets hinter mapping from imager CTM and font matrices, scale/subpixel values, origin, and alignment-to-pixels setting.
- Loads Type 1 font data into the hinter with grid-fitting control.
- Maintains operand stack `cstack`, charstring instruction stack `ipstack`, decryption state, current instruction pointer, and origin.

## Number Decoding
- Decodes Type 1 one-byte, two-byte positive/negative, and four-byte numeric encodings.
- Handles rare oversized four-byte values by recognizing an immediate denominator followed by `escape div` and pushing a fixed-point quotient.
- Pushes decoded fixed-point values to the charstring operand stack with stack overflow checks via macros from Type 1 internals.

## Main Operators
- `callsubr`: applies `subroutineNumberBias`, obtains subroutine data via `pdata->procs.subr_data`, saves current IP/decryption state, and enters the subroutine.
- `return`: frees current glyph data and resumes previous instruction stack frame.
- Stem/path ops (`hstem`, `vstem`, `rmoveto`, `rlineto`, `rrcurveto`, `vhcurveto`, `hvcurveto`, `closepath`) call `t1_hinter__*`.
- `endchar`: ends hinting, optionally handles `seac` accent flow, sets current point from path, and calls `gs_type1_endchar`.
- `hsbw` and escaped `sbw`: set side bearing/width via hinter and `gs_type1_sbw`, save interpreter continuation state, and return `type1_result_sbw` so the client may intervene.

## Escape Operators
- `dotsection`, `vstem3`, `hstem3`: delegate to hinter.
- `seac`: calls `gs_type1_seac`; may return to caller with accent index or restart with composed glyph data.
- `div`: divides top operands.
- `callothersubr`: implements recognized OtherSubrs internally:
  - 0, 1, 2: Flex begin/points/end.
  - 3: drop hints.
  - 12, 13: counter control ignored.
  - 14-18: Multiple Master blend with 1, 2, 3, 4, or 6 results.
  - Unrecognized OtherSubrs copy arguments to the caller through `push_values`, save interpreter state/operand stack, store the OtherSubr number in `*pindex`, and return `type1_result_callothersubr`.
- `pop`: either consumes ignored pops after known OtherSubrs or obtains a value from caller callback `pop_value`.
- `setcurrentpoint`: updates hinter current point and applies accent displacement.

## Dependencies
Depends on Type 1 font data (`gxfont1.h`, `gxtype1.h`), Type 1 encryption macros, glyph data management, fixed-point arithmetic, imager/path state, and the Type 1 hinter API in `gxhintn.h`.

## Risks and Notes
- The interpreter trusts many helper macros and callback contracts for stack bounds, data lifetime, and glyph/subroutine lookup.
- Some historical font compatibility hacks are explicit: `undoc15`, Flex handling, Fontographer side-bearing adjustment during `seac`.
- Counter control OtherSubrs are not implemented.
