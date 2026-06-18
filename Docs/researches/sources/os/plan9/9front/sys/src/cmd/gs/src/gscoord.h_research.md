# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscoord.h

## Role

`gscoord.h` declares the Ghostscript graphics-state CTM and coordinate transformation API.

This is graphics geometry API infrastructure, not filesystem code.

## Public API

- CTM modification:
  - `gs_initmatrix`
  - `gs_defaultmatrix`
  - `gs_currentmatrix`
  - `gs_setmatrix`
  - `gs_translate`
  - `gs_scale`
  - `gs_rotate`
  - `gs_concat`
- Extensions:
  - `gs_setdefaultmatrix`
  - `gs_currentcharmatrix`
  - `gs_setcharmatrix`
  - `gs_settocharmatrix`
- Transform operations:
  - `gs_transform`
  - `gs_dtransform`
  - `gs_itransform`
  - `gs_idtransform`
- Imager-state operations:
  - `gs_imager_setmatrix`
  - `gs_imager_idtransform`

## Dependencies

Requires `gsmatrix.h` and `gsstate.h` context; forward-declares `gs_imager_state` if needed.

## Notable Risks

Header only; behavior and cache invalidation are in `gscoord.c`.
