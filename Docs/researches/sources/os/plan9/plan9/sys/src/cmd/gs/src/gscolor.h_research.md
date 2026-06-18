# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscolor.h

## Purpose
Public client interface for basic color and transfer routines.

## Key Contents
- Declares gray/RGB/null color routines:
  - `gs_setgray`,
  - `gs_currentgray`,
  - `gs_setrgbcolor`,
  - `gs_currentrgbcolor`,
  - `gs_setnullcolor`.
- Declares transfer-function routines:
  - `gs_settransfer`,
  - `gs_settransfer_remap`,
  - `gs_currenttransfer`.

## Dependencies
Includes `gxtmap.h` for transfer mapping types.

## Research Notes
Some declared current-color routines are implemented elsewhere, not in `gscolor.c`.
