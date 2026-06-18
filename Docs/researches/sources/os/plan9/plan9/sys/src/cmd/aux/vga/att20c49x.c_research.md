# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/att20c49x.c

RAMDAC backend for ATT20C490 and ATT20C491/492 true-color CMOS RAMDACs.

Core behavior:
- Parses optional speed grade suffix from controller name, defaulting to 55 MHz.
- Ensures requested pixel clock does not exceed part grade.
- Puts `att20c491`/`att20c492` into sleep briefly before writing mode.
- Writes control register 0 with base mode; 8-bit color control is present but disabled by `&& 0`.

Ctlrs:
- `att20c490`
- `att20c491`
- `att20c492`

Dependencies:
- Uses `attdaci()` and `attdaco()` accessors provided by `att21c498.c`.

Notable risks:
- The `if(vga->f == 0)` check appears to test the array pointer rather than `vga->f[0]`, likely a bug or old-compiler idiom mistake.
