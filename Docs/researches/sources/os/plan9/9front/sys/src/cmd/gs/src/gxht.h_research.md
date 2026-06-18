# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxht.h

## Role

`gxht.h` defines client-facing Ghostscript halftone structures, including spot, threshold, extended threshold, client-order, component, multiple, and union halftone objects.

This is imaging/halftone infrastructure, not filesystem code.

## Main Types

- `gs_spot_halftone`: Type 1 halftone with screen parameters, AccurateScreens flag, and transfer closure.
- `gs_threshold_halftone_common`: shared width/height/transfer closure fields for threshold halftones.
- `gs_threshold_halftone`: Type 3 threshold halftone with byte thresholds.
- `gs_threshold2_halftone`: extended Type 3 threshold halftone with one/two-byte samples and one/two rectangles.
- `gs_client_order_halftone`: client-defined halftone that creates a `gx_ht_order`.
- `gs_halftone_component`: Type 5 component with component number/name, type, and per-type params.
- `gs_multiple_halftone`: Type 5 halftone with component array and color-name callback.
- `gs_halftone`: ref-counted graphics-state halftone union covering setscreen, setcolorscreen, Type 1, Type 3, extended Type 3, client order, and Type 5.

## Public Interface

- AccurateScreens globals: `gs_setaccuratescreens`, `gs_currentaccuratescreens`.
- UseWTS globals: `gs_setusewts`, `gs_currentusewts`.
- Screen sampling: `gs_screen_init_memory` and `gs_screen_init_accurate`.
- MinScreenLevels globals: `gs_setminscreenlevels`, `gs_currentminscreenlevels`.

## Important Notes

- The header explicitly states client halftone data may be relocated by GC but will not be freed on halftone release; clients own that memory.
- User-provided data is expected to be heap-allocated so Ghostscript GC can treat it as a structure pointer.
- Generalized halftone cache keys are difficult because device-specific halftone representation can depend on device transform and device color sense.

## Notable Risks

- Some fields are marked obsolete (`transfer`) but still present for compatibility.
- Lifetime rules for client data are subtle and easy to violate.
- Halftone objects intentionally lack stable ids suitable for generalized cache keys.
