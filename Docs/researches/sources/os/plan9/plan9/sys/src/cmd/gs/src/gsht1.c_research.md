# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht1.c

Implements extended halftone operators: `setcolorscreen`, `currentcolorscreen`, `sethalftone`, allocated halftone installation, and preparation of multiple halftone types.

Supported halftone preparation paths:
- Type 2 colorscreen: samples gray/red/green/blue screens and maps names to device components.
- Spot halftones: delegates screen sampling to `gx_ht_process_screen_memory`.
- Threshold halftones: builds threshold orders from byte threshold arrays.
- Threshold2 halftones: supports two rectangles and 1- or 2-byte samples, reducing level count to a maximum of 14 bits.
- Client order halftones: delegates order creation to client callbacks.
- Multiple and multiple-colorscreen halftones: validates/defaults components and builds a component array.

Transfer handling:
- `process_transfer` builds a `gx_transfer_map` when a procedural or closure transfer is supplied.
- Transfer maps are initialized with `load_transfer_map` and attached to `gx_ht_order`.

WTS path:
- `gs_sethalftone_try_wts` opportunistically creates WTS-based device halftones for Type 5 multiple halftones.
- It only accepts accurate spot components and separable/linear or monochrome bilevel devices.
- The function creates WTS enumerators and records them in component orders for later conversion during install.

Risks and quirks:
- The WTS path has a comment noting missing cleanup on error.
- Multiple halftones require exactly one Default; duplicates or absence result in `rangecheck`.
- Threshold2 reduces precision when too many levels are present.
