# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstate.h

Declares the public graphics-state API.

Key declarations:
- Opaque `gs_state` and overprint parameter forward declaration.
- Allocation/free and save/restore/copy APIs: `gs_state_alloc`, `gs_state_free`, `gs_gsave`, `gs_grestore`, `gs_grestoreall`, `gs_gstate`, `gs_state_copy`, `gs_copygstate`, `gs_currentgstate`, and `gs_setgstate`.
- Save/restore helpers used by interpreter `save`/`restore`.
- Overprint controls and `gs_do_set_overprint`.
- `gs_initgraphics`.
- Includes public device, line, color, halftone, and color-selection headers.
- Screen/halftone phase APIs and miscellaneous fill-adjust, limit-clamp, text-rendering-mode, and cache-device accessors.

Research notes:
- This header is a broad facade: including it also brings in major public graphics-state sub-APIs.
