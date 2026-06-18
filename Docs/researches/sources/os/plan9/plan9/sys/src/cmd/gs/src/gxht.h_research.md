# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxht.h

Purpose: declares client-side halftone structures and public halftone control APIs.

Halftone types modeled:
- Type 1 spot halftones: `gs_spot_halftone`.
- Type 3 threshold halftones: `gs_threshold_halftone`.
- Extended Type 3 threshold halftones: `gs_threshold2_halftone`.
- Client-defined order halftones: `gs_client_order_halftone`.
- Type 5 multi-component halftones: `gs_multiple_halftone`.
- Unified graphics-state halftone union: `gs_halftone`.

Important design comments:
- Halftones are not globally identified/cache-keyed objects in this library design.
- Client-provided data can be relocated by GC, but clients remain responsible for freeing it.
- General halftone caching is device-dependent because spot halftone representation depends on device transformation and additive/subtractive sense.

Memory/GC support:
- Declares structure descriptors and max pointer counts for halftone components and whole halftones.

Procedural APIs:
- `gs_setaccuratescreens` / `gs_currentaccuratescreens`.
- `gs_setusewts` / `gs_currentusewts`.
- `gs_screen_init_memory` and `gs_screen_init_accurate`.
- `gs_setminscreenlevels` / `gs_currentminscreenlevels`.

Research notes:
- This header is the main structural contract for halftone objects used by PostScript graphics state and device setup.
