# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsht1.h

## Role

`gsht1.h` extends the public halftone API with color screens and general `gs_halftone` installation/query routines.

This is graphics API infrastructure, not filesystem code.

## Main Declarations

- `gs_setcolorscreen`, `gs_currentcolorscreen`.
- Opaque `gs_halftone` forward declaration.
- `gs_sethalftone`, `gs_sethalftone_allocated`, `gs_currenthalftone`.

## Important Contract

`gs_sethalftone` assumes the halftone and all substructures were allocated with the same allocator as the graphics state. `gs_sethalftone_allocated` reads the allocator from the halftone's `rc.memory`. Both copy the top-level structure but take ownership of substructures.

## Notable Risks

The ownership contract is easy to misuse: callers must not free substructures after successful installation, but may need to clean up remaining referenced data after failure depending on the lower-level install path.
