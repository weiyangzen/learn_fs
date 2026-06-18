# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgatvp3020.c

## Purpose
Hardware cursor support for the TI TVP3020 Viewpoint Video Interface Palette, assumed to be attached to an S3 86C928.

## Main Interfaces
- Exports `VGAcur vgatvp3020cur` named `tvp3020hwgc`.
- Provides enable, disable, load, and move callbacks for the VGA cursor layer.

## Implementation Notes
- Indirect DAC access is selected through S3 CRTC register `0x55`, using the lower DAC register bits to choose VGA palette ports.
- `tvp3020enable` initializes cursor control, overscan/cursor colors, and S3 external cursor control bits.
- `tvp3020load` writes a 64x64 cursor RAM image, placing the 16x16 Plan 9 cursor in the top-left and zeroing the remainder.
- Cursor image bits are expanded into 2-bit-per-pixel X-Windows cursor mode.
- `tvp3020move` writes low/high X and Y cursor position registers.

## Dependencies And Risks
- Tight coupling to S3 VGA indexed registers `Crtx 0x45` and `0x55`.
- Assumes 16x16 Plan 9 cursor source and 64x64 hardware cursor RAM.
- Does not probe or validate the DAC; selection is by configured cursor device.
