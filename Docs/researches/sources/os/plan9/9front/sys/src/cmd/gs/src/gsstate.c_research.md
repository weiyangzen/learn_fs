# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsstate.c

Implements Ghostscript graphics-state allocation, lifetime management, save/restore, copy/current/setgstate, overprint updates, and miscellaneous state operators.

Key behavior:
- The large opening comment classifies all state-owned storage: embedded state, GC-owned references, ref-counted shared members, stack-associated objects, per-state heap objects, and client data.
- Defines `gs_state` GC enumeration/relocation, including special handling for devices and device-filter stacks.
- `gs_state_alloc` allocates an initial state, initializes imager state, paths, clip paths, view clip, color space/color, null device, alpha/transfer/line defaults, font placeholders, and a bottom save.
- `gs_gsave`, `gs_grestore_only`, `gs_grestore`, `gs_gsave_for_save`, `gs_grestoreall_for_restore`, and `gs_grestoreall` implement graphics-state stack manipulation and save-level view-clip behavior.
- `gs_gstate`, `gs_state_copy`, `gs_copygstate`, `gs_currentgstate`, and `gs_setgstate` clone or copy states with distinct semantics for saved pointers, view clips, client data, and show-state pointers.
- `gstate_alloc_parts`, `gstate_clone`, `gstate_free_contents`, and `gstate_copy` handle per-state path/clip/color/device-color allocations, shared path segments, dash patterns, refcounts, and color-space counts.
- Overprint APIs update overprint flags/mode and install or refresh an overprint compositor through device `create_compositor`.
- `gs_initgraphics` resets matrix, path, clipping, line parameters, dash state, dot settings, miter limit, and RasterOp defaults without resetting current color/color space.
- Includes fill adjust, coordinate clamp, and text rendering mode accessors.

Dependencies:
- Ties together imager state, devices, paths, clip paths, color spaces, pattern caches, halftones, line state, overprint compositor, and client callbacks.

Research notes:
- This file is the central ownership boundary for graphics-state mutation.
- State copy operations are deliberately subtle: `gsave` switches old/new private parts, while off-stack clones keep their own parts.
- Overprint compositor refresh is required after state restoration and `setgstate` when overprint state may change.
