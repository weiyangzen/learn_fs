# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht.h

## Role

`gsht.h` is the public Ghostscript Type 1 and color screen halftone interface.

This is graphics API infrastructure, not filesystem code.

## Main Declarations

- `gs_screen_halftone`: frequency, angle, spot function, and actual selected frequency/angle.
- `gs_colorscreen_halftone`: four screen definitions addressable as indexed entries or red/green/blue/gray fields.
- Procedural API: `gs_setscreen`, `gs_currentscreen`, `gs_currentscreenlevels`.
- Screen enumeration API: `gs_screen_enum_alloc`, `gs_screen_init`, `gs_screen_currentpoint`, `gs_screen_next`, and `gs_screen_install`.

## Important Contract

The enumeration API requires clients to initialize an enumerator, repeatedly request the current sample point and supply the spot function result, then optionally install the sampled screen. The comments explicitly describe this as an enumeration-style definition of a single screen.

## Notable Risks

The header exposes callback-driven spot functions and incremental enumeration; callers must keep the `gs_state`, allocator, and screen structure valid for the full sampling/install sequence.
