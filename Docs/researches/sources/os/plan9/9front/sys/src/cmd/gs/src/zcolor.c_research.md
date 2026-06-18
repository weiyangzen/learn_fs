# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcolor.c

This file implements core color and color-space operators.

Key behavior:
- `currentcolor` returns numeric color components and, for pattern spaces, the pattern dictionary or null object.
- `currentcolorspace` returns the interpreter’s stored color-space array, with special handling to synthesize `DeviceGray` when necessary.
- `.getuseciecolor` reads the interpreter state flag corresponding to `UseCIEColor`.
- `setcolor` gathers numeric and pattern operands and passes them to `gs_setcolor`.
- `setcolorspace` stores the nominal PostScript color-space array in interpreter state.
- `.setdevcspace` sets DeviceGray, DeviceRGB, or DeviceCMYK via graphics-library color-space initialization.
- Implements `currenttransfer`, `settransfer`, and color remapping helpers that sample transfer procedures into transfer maps.
- Provides internal color remap/reset operators and diagnostic `.color_test` / `.color_test_all`.

Important dependencies:
- Uses graphics color APIs from `gxcolor2.h`, `gxcspace.h`, `gxcmap.h`, `gxdcolor.h`, and `gxpcolor.h`.
- Uses e-stack sampling through `zfor_samples`.
- Relies on `gx_set_effective_transfer` from halftone/transfer logic.

Research notes:
- This file owns interpreter color state synchronization with graphics state.
- Several operators are internal and invoked under controlled PostScript initialization paths rather than doing full operand validation.
