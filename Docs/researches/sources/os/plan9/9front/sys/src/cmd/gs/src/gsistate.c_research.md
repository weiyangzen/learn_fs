# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsistate.c

Implements Ghostscript imager-state housekeeping: GC descriptors, initialization, shallow copying, reference-count adjustment, pre-assignment, and release.

Key behavior:
- Defines GC enumeration/relocation for `gx_line_params`, including dash pattern relocation.
- Defines `public_st_imager_state()` traversal for client data, opacity/shape masks, transparency stack, CR state pointers, and effective transfer maps.
- `gs_imager_state_initialize` initializes memory, rendering/color fields, transfer maps, screen phases, pattern state, and default color-map procedures.
- Allocates one identity gray transfer map and shares it through all `effective_transfer` entries.
- `gs_imager_state_copy` performs a shallow struct copy but clears `transparency_stack`, explicitly noting incomplete reference-count handling.
- `gs_imager_state_copied`, `gs_imager_state_pre_assign`, and `gs_imager_state_release` manage reference-counted members such as masks, halftones, CIE rendering, transfer maps, and joint caches.
- Release has special handling for `dev_ht`: if the device halftone refcount is about to drop to zero, dependent halftone structures are released first.

Dependencies:
- Uses Ghostscript GC/reference-count macros from `gsstruct.h` and related imager/color headers.
- Imports `cmap_procs_default`.
- Uses `gs_next_ids` for transfer-map identity allocation.

Research notes:
- This file is central to safe state lifetime management for imaging operations.
- The shallow-copy API is intentionally limited and should not be treated as a fully independent clone without later `gs_imager_state_copied`/assignment handling.
