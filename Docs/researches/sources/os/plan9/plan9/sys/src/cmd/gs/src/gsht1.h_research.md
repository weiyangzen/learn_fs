# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsht1.h

Extended public halftone API.

Exports:
- `gs_setcolorscreen`
- `gs_currentcolorscreen`
- `gs_sethalftone`
- `gs_sethalftone_allocated`
- `gs_currenthalftone`

Documents ownership expectations:
- `gs_sethalftone` assumes the halftone and substructures use the same allocator as the `gs_state`.
- `gs_sethalftone_allocated` uses `rc.memory` from the halftone.
- Both copy the top-level structure but take ownership of substructures.

This header bridges Level 1-style screen APIs from `gsht.h` with Level 2 halftone dictionaries.
