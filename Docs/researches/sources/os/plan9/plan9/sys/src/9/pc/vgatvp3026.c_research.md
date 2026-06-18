# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgatvp3026.c

## Purpose
Hardware cursor support for the TI TVP3026 Viewpoint Video Interface Palette, assumed to be attached to an S3 Vision968.

## Main Interfaces
- Exports `VGAcur vgatvp3026cur` named `tvp3026hwgc`.
- Exports `tvp3026xo`, an indirect register writer likely shared with other TVP3026-related code.

## Implementation Notes
- Uses CRTC register `0x55` to select DAC indexed-register windows.
- `tvp3026enable` enables direct cursor control, writes overscan and cursor colors, and turns on 3-color cursor mode.
- `tvp3026load` writes separate 64x64 cursor planes: all `clr` bytes first, then all `set` bytes.
- Hardware origin is bottom-right-oriented, so load stores `scr->offset` as `64 + curs->offset`.
- `tvp3026move` adds `scr->offset` before writing cursor position registers.

## Dependencies And Risks
- Depends on S3 DAC routing behavior and the TVP3026 direct cursor registers.
- Cursor memory layout differs from TVP3020 and is not interchangeable.
- No runtime validation of DAC presence or cursor RAM behavior.
