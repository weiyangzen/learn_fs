# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstate.c

## Purpose
Implements Ghostscript graphics-state lifecycle, save/restore stack behavior, copying, overprint updates, initialization, and miscellaneous state controls.

## Public Surface
- Allocation/free: `gs_state_alloc`, `gs_state_free`.
- Save/restore: `gs_gsave`, `gs_grestore`, `gs_grestore_only`, `gs_gsave_for_save`, `gs_grestoreall_for_restore`, `gs_grestoreall`.
- Copying: `gs_gstate`, `gs_state_copy`, `gs_copygstate`, `gs_currentgstate`, `gs_setgstate`.
- Accessors/swaps: `gs_state_memory`, `gs_state_saved`, `gs_state_swap_saved`, `gs_state_swap_memory`, `gx_get_clip_path_id`.
- Overprint: `gs_state_update_overprint`, `gs_do_set_overprint`, `gs_setoverprint`, `gs_currentoverprint`, `gs_setoverprintmode`, `gs_currentoverprintmode`.
- Initialization and misc: `gs_initgraphics`, `gs_setfilladjust`, `gs_currentfilladjust`, `gs_setlimitclamp`, `gs_currentlimitclamp`, `gs_settextrenderingmode`, `gs_currenttextrenderingmode`.

## Storage Model
The file documents graphics-state storage ownership in detail:
- The `gs_state` object itself is stack-owned.
- Some pointers are GC-managed and not reference-counted, such as fonts/devices in some contexts.
- Shared objects such as halftones, color rendering, transfer functions, clip stacks, and masks are reference-counted.
- Per-state private objects include path, clip paths, color space, client color, device color, and dash pattern.
- Path/clip/color sub-objects require custom reference or count adjustment when copied.

## Allocation and Initialization
- `gs_state_alloc` creates a state, initializes the imager state, halftone, path, clip/view/effective clip paths, default DeviceGray color space, null device, alpha, transfer, flatness, fill adjust, line settings, font placeholders, and transparency stack fields.
- Paths use stable memory through `gstate_path_memory` to survive `save ... restore` patterns involving Type 3 `setcachedevice`.
- `gs_initgraphics` resets matrix, path, clipping, line parameters, dash/dot settings, miter limit, and RasterOp state, but intentionally does not reset color or color space.

## Save/Restore Control Flow
- `gs_gsave` clones the current state, clears the cloned clip stack, increments the device-filter stack, links it as `pgs->saved`, and increments level.
- `gs_gsave_for_save` additionally clones view clipping, then cuts the stack so `grestore` cannot cross a PostScript `save` boundary.
- `gs_grestore_only` restores the saved state by swapping client data, copying client data for grestore, freeing current contents, assigning from saved, preserving transparency stack, freeing the saved shell, and updating overprint when needed.
- `gs_grestore` maintains the invariant that at least one saved state remains on the stack by doing a new `gsave` after bottom restore.
- `gs_grestoreall_for_restore` unwinds to the save boundary, frees pattern cache contents to avoid dangling references, splices the old stack, drops view clip, and restores twice.

## Copy/Clone Internals
- `gstate_alloc_parts` allocates or shared-allocates path and clipping structures, private color space, client color, and device color.
- `gstate_clone` copies the full state, duplicates dash patterns, copies client data through client callbacks, increments device refs, swaps private parts for `gsave`, and adjusts color-space reference counts.
- `gstate_copy` copies one allocated state into another while preserving destination allocator, saved pointer, pattern cache fallback, dash storage, and client data.
- `gstate_free_contents` decrements ref-counted device/clip/filter stacks, adjusts color-space counts, frees client data, dash pattern, private parts, and releases imager-state contents.

## Overprint
- `gs_state_update_overprint` creates an overprint compositor and asks the current device to create/update a compositor device; if a new device is returned it becomes current.
- `gs_do_set_overprint` delegates to pattern color handling or color-space `set_overprint`, depending on current color space and pattern state.
- Overprint mode is range-checked to 0 or 1 and triggers recomputation only when active and changed.

## Dependencies
This file is central to Ghostscript graphics state and depends on imager state, paths, clip paths, devices, halftones, color spaces, pattern cache, overprint compositors, line state, and memory/reference-count utilities.

## Risks and Notes
- The save/restore logic is ownership-sensitive; incorrect changes can double-free paths, lose client data, or leave dangling clip/pattern references.
- `gs_setgstate` temporarily nulls view clip to prevent refcount decrementing, then restores saved state metadata.
- The file carries historical compatibility decisions, including color not being reset by `initgraphics`.
