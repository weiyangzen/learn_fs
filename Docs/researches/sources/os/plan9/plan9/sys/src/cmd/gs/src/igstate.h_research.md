# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igstate.h

Defines interpreter-specific graphics state data layered on top of library `gs_state`.

Key points:
- The interpreter treats the library graphics state mostly as opaque, but attaches client data made of refs.
- Defines `igstate_obj`, a wrapper used for gstate objects so save/restore can manipulate an intermediate object instead of copying full `gs_state`s.
- Defines ref-bearing parameter groups for DeviceN, CIE, CIE rendering, Separation, and Indexed color procedures.
- Defines `ref_colorspace` for the current color-space array and associated procedure refs.
- Defines `int_gstate`, containing refs for dash pattern, screen and transfer procedures, black generation, undercolor removal, colorspace, pattern, color rendering, UseCIEColor, halftone, pagedevice, remap color info, opacity mask, and shape mask.
- Provides `int_gstate_map_refs` for GC enumeration.
- Declares `int_gstate_alloc`.
- Defines `gs_int_gstate`, `igs`, and `istate` helpers.

Research relevance:
- Captures interpreter-visible graphics state refs that must participate in GC, save/restore, color remapping, halftones, page devices, and transparency state.
