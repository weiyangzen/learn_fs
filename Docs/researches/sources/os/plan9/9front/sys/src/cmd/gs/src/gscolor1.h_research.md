# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor1.h

## Role

`gscolor1.h` declares the client interface for Ghostscript Level 1 extended color facilities.

This is rendering/color API infrastructure, not filesystem code.

## Public API

- `gs_setcmykcolor`
- `gs_currentcmykcolor`
- `gs_setblackgeneration`
- `gs_setblackgeneration_remap`
- `gs_currentblackgeneration`
- `gs_setundercolorremoval`
- `gs_setundercolorremoval_remap`
- `gs_currentundercolorremoval`
- `gs_setcolortransfer`
- `gs_setcolortransfer_remap`
- `gs_currentcolortransfer`

## Dependencies

Requires `gscolor.h` context and Ghostscript mapping-procedure types.

## Notable Risks

Header-only declarations; behavior and reference-count safety are in `gscolor1.c`.
