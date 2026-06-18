# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht1.c

## Role

`gsht1.c` implements extended Ghostscript halftone operators: `setcolorscreen`, `sethalftone`, Level 2/Type 5 multiple halftones, threshold halftones, client-order halftones, transfer override construction, and a WTS fast path.

This is rendering halftone infrastructure, not filesystem code.

## Main Interfaces

- Public API: `gs_setcolorscreen`, `gs_currentcolorscreen`, `gs_sethalftone`, `gs_sethalftone_allocated`, `gs_sethalftone_prepare`, `gx_ht_complete_threshold_order`, `gx_ht_construct_threshold_order`.
- Internal processors: `process_transfer`, `process_spot`, `process_threshold`, `process_threshold2`, `process_client_order`, `gs_sethalftone_try_wts`.
- Defines GC pointer handling for `gs_halftone_component` values.

## Core Behavior

- `gs_setcolorscreen` wraps a `gs_colorscreen_halftone` as a `ht_type_colorscreen` and delegates to `gs_sethalftone`.
- `gs_sethalftone_prepare` converts high-level halftone definitions into a transient `gx_device_halftone` with a default order plus optional component orders.
- Spot components are sampled through `gx_ht_process_screen_memory`; threshold components allocate threshold orders and sort threshold values into level boundaries; client orders delegate construction to client procs.
- Extended threshold2 halftones can combine two rectangles, compute a strip geometry from their heights, reduce 16-bit thresholds to a bounded level count, and build a single threshold order.
- Multiple halftones require exactly one `Default` component and can include spot, threshold, threshold2, or client-order components.
- Transfer overrides allocate a reference-counted `gx_transfer_map`, load it with `load_transfer_map`, and attach it to the order.
- `gs_sethalftone_try_wts` attempts a well-tempered screen path only for Type 5 multiple spot halftones, accurate screens, and compatible bilevel/separable devices.

## Notable Risks

- The WTS path contains a `todo: cleanup on error`; partial allocations and transfer maps can leak if setup fails mid-loop.
- `gs_sethalftone_prepare` frees only the component array on some errors; any per-component order substructures created before the error rely on later callers or code paths for cleanup.
- Threshold2 intentionally drops low-order threshold bits when the level count would exceed `MAX_HT_LEVELS`, which can lose information.
- Multiple halftone validation depends on a single `Default` component and positional assumptions around the component array.
