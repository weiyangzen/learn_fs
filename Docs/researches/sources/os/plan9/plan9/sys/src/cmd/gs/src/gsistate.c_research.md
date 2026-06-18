# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsistate.c

Implements Ghostscript imager-state housekeeping. It defines GC pointer enumeration and relocation for `gx_line_params` dash patterns and `gs_imager_state`, including client data, opacity/shape masks, transparency stack, color rendering pointers, and effective transfer maps.

`gs_imager_state_initialize` seeds a new imager state with memory ownership, null color rendering and transparency references, default screen phases, a newly allocated identity gray transfer map, default color-map procedures, and pattern-cache defaults. `gs_imager_state_copy` performs a shallow temporary copy and clears the transparency stack in the copy.

Reference-count lifecycle is explicit: `gs_imager_state_copied` increments referenced masks, halftones, transfer maps, CIE state, and caches; `gs_imager_state_pre_assign` uses `rc_pre_assign` before assignment; `gs_imager_state_release` decrements the same references and specially releases dependent device-halftone structures when the last reference is about to go away.

Key dependencies: `gxistate.h`, `gzline.h`, transfer maps, CIE rendering structures, device halftone release, and Ghostscript reference-count macros. This file is central to safe copying and teardown of graphics/imager state.
