# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcolor.c

Implements core color, colorspace, transfer, and color-device test operators.

Key behavior:
- `currentcolor` pushes numeric components and optional pattern dictionary/null for pattern color spaces; integral values are pushed as integers.
- `currentcolorspace` returns the interpreter-tracked colorspace array and normalizes DeviceGray fallback behavior.
- `.getuseciecolor` reads interpreter `UseCIEColor` state.
- `setcolor` gathers numeric and optional pattern operands and calls `gs_setcolor`.
- `setcolorspace` records the nominal PostScript colorspace array; `.setdevcspace` installs DeviceGray/RGB/CMYK in the graphics state.
- `currenttransfer`, `settransfer`, and shared remapping helpers sample PostScript transfer procedures into graphics transfer maps via estack sampling loops.
- `.color_test` and `.color_test_all` exercise device encode/decode color behavior and report worst errors through debug output.
- `.includecolorspace` asks the graphics layer whether a named colorspace should be included for high-level device output.

Dependencies and coupling:
- Shared remap helpers are used by `zcolor1.c`.
- Uses `zfor_samples` and estack continuations to sample procedures.
- Maintains interpreter-side refs for transfer procedures and pattern dictionaries in `istate`.
