# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor.h

## Role

`gscolor.h` declares the base Ghostscript client color API for gray/RGB/null color and transfer functions.

This is rendering/color API infrastructure, not filesystem code.

## Public API

- `gs_setgray`
- `gs_currentgray`
- `gs_setrgbcolor`
- `gs_currentrgbcolor`
- `gs_setnullcolor`
- `gs_settransfer`
- `gs_settransfer_remap`
- `gs_currenttransfer`

## Dependencies

Includes `gxtmap.h` for transfer-map procedure types.

## Notable Risks

This header only declares APIs; current-color query implementations are elsewhere.
