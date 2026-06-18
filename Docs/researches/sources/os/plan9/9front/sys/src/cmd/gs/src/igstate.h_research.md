# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/igstate.h

Defines interpreter-specific graphics state data layered on top of library `gs_state`.

Key points:
- The library graphics state is mostly opaque to the interpreter, but the interpreter attaches client data made of refs.
- Defines `igstate_obj`, a wrapper ref structure used for gstate objects so save/restore can manipulate an intermediate object rather than copying full `gs_state`s.
- Defines helper macro `igstate_ptr`.
- Defines ref-bearing parameter groups for:
  - DeviceN names/tint transform
  - CIE decode/procedure refs
  - CIE rendering transforms
  - Separation name/tint transform
  - Indexed color procedure
- Defines `ref_colorspace` holding the current color space array and associated procedure refs.
- Defines `int_gstate`, containing refs for:
  - dash pattern
  - screen and transfer procedures
  - black generation and undercolor removal
  - colorspace and pattern
  - color rendering dictionary/procs
  - UseCIEColor
  - halftone
  - pagedevice
  - remap color info
  - opacity and shape masks
- Provides `int_gstate_map_refs` for enumerating refs in the structure.
- Declares `int_gstate_alloc`.
- Defines `gs_int_gstate`, `igs`, and `istate` helpers.

Dependencies and interactions:
- Used by graphics-state operators and color/halftone/page-device code.
- Tied to `e_RemapColor` in `ierrors.h`.

Research relevance:
- Captures all interpreter-visible graphics state refs that must participate in GC and save/restore.
