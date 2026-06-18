# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcssepr.c

Implements Separation color-space and overprint operators.

Key behavior:
- Defines `.setseparationspace`, `currentoverprint`, `setoverprint`, `.currentoverprintmode`, and `.setoverprintmode`.
- Treats Separation as a single-component DeviceN-like space except for `/All` and `/None`.
- Validates separation name, alternate color space, tint-transform procedure, and tint function.
- Builds a Separation space, records the separation name/type, installs `gs_cspace_set_sepr_function`, and updates interpreter color-space procedure refs.
- Provides direct wrappers for overprint flag and overprint mode in graphics state.

Dependencies:
- Uses name-table operations, Separation/DeviceN graphics-library structures, function extraction, and interpreter graphics state.

Research notes:
- Like DeviceN, failure paths restore the previous interpreter color-space refs and free the allocated separation map.
