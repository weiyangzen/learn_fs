# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsstate.h

## Purpose
Declares the public Ghostscript graphics-state API for allocation, save/restore, copy/setgstate, overprint, graphics initialization, device/color/halftone/line controls, and miscellaneous state fields.

## Public Surface
- Opaque `gs_state`.
- Opaque `gs_overprint_params_t`.
- Lifecycle: `gs_state_alloc`, `gs_state_free`.
- Save/restore/copy: `gs_gsave`, `gs_grestore`, `gs_grestoreall`, `gs_grestore_only`, `gs_gsave_for_save`, `gs_grestoreall_for_restore`, `gs_gstate`, `gs_state_copy`, `gs_copygstate`, `gs_currentgstate`, `gs_setgstate`.
- Overprint: `gs_state_update_overprint`, `gs_currentoverprint`, `gs_setoverprint`, `gs_currentoverprintmode`, `gs_setoverprintmode`, `gs_do_set_overprint`.
- Initialization: `gs_initgraphics`.
- Halftone phase: `gs_setscreenphase`, `gs_currentscreenphase`, `gx_imager_setscreenphase`, plus `gs_sethalftonephase` and `gs_currenthalftonephase` macros.
- Misc: fill adjust, limit clamp, text rendering mode, cache-device status.

## Dependencies
Includes downstream public headers for devices, lines, colors, halftone screens, color selection, color pattern/mask support, and cache-device mode.

## Risks and Notes
- This header intentionally exposes a broad graphics-state surface while keeping the structure opaque. Internal code requiring fields uses `gzstate.h` instead.
