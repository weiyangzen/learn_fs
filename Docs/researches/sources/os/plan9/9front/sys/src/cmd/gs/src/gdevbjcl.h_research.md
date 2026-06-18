# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbjcl.h

## Purpose
Declares the Canon BJC command-generation library and printer capability masks.

## Capability Model
- Defines bit flags for optional command support:
  - single-character commands
  - session commands
  - page commands
  - resolution modes
  - image commands
- Defines model capability masks for BJC 50, 70, 80, 210, 250, 610, 620, 4000, 4100, 4200, 4300, 4550, 4650, 5500, and 7000.
- Provides `BJC_ENUMERATE_OPTIONS(m)` to build tables over known models.

## Command API
Declares command emitters for:
- CR, FF, LF
- initialize / initial condition
- print method
- media supply
- identify cartridge
- page margins and extended margins
- page ID
- raster compression
- raster resolution and skips
- CMYK raster image
- move lines and movement unit
- image format and photo image
- continue image
- indexed image

## Types
Defines enums for print color, media, quality, black density, short print modes, media supply/type, cartridge commands, compression, CMYK components, image format, and ink system.

## Notes
- Several comments mark commands as model-specific or “different for 7000”.
- Header declares `bjc_put_initial_condition` and `bjc_put_compression`, while `gdevbjcl.c` implements `bjc_put_set_initial` and `bjc_put_set_compression`; this mismatch is important if these APIs are compiled/linked directly.
