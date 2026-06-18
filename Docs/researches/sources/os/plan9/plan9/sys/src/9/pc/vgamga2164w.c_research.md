# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgamga2164w.c

Matrox Millennium/Millennium II MGA2064W/MGA2164W device mapping and TI TVP3026 RAMDAC hardware cursor support. `mgapcimatch()` prefers MGA2164AGP, then MGA2164, then MGA2064.

`mga2164wenable()` maps the correct MMIO BAR depending on chip generation, exports `mga2164wmmio`, and maps framebuffer aperture as 8MB for MGA2064 or 16MB for later devices.

TVP3026 cursor support:
- Uses MMIO DAC window at offset `0x3C00`.
- `tvp3026disable()` forces cursor off and direct control.
- `tvp3026enable()` sets overscan and cursor colors, loads arrow, and enables 64x64 3-color mode.
- `tvp3026load()` writes two cursor RAM planes and sets hotpoint as `64 + offset`.
- `tvp3026move()` writes cursor X/Y low/high registers.

Exports `VGAdev vgamga2164wdev` and `VGAcur vgamga2164wcur`.
