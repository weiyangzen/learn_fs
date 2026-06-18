# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjcl.c

## Purpose
Implements a small command-generation library for Canon BJC-family printer command streams.

## Main Helpers
- `bjc_put_bytes`
- `bjc_put_hi_lo`
- `bjc_put_lo_hi`
- `bjc_put_command`

These write command bytes to Ghostscript `stream` objects with the expected byte ordering.

## Commands Implemented
- Single-byte controls: LF, FF, CR.
- Initialization: return to initial condition and set initial condition.
- Data compression selection.
- Print method selection, short and extended.
- Raster resolution.
- Raster skip.
- Page margins and extended margins.
- Media supply.
- Ink cartridge identification.
- CMYK raster image data.
- Move by raster lines and set movement unit.
- Image format.
- Page ID.
- Continue raster image.
- BJ indexed image.

## Behavior
Each public function emits a concrete BJC escape sequence and payload. The implementation does not validate model capabilities; callers are expected to know which commands a target printer supports.

## Dependencies
Uses `std.h`, `gdevbjcl.h`, and Ghostscript `stream` write helpers.
