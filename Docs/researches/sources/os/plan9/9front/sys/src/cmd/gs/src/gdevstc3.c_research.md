# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevstc3.c

Sample RGB “dithering” module for the Epson Stylus Color driver.

Key behavior:
- Implements `stc_gsrgb`, selected with `-sDithering=gsrgb`.
- Does not perform real dithering; it expects Ghostscript to supply simple RGB byte values.
- Converts three input bytes per pixel into a single output byte with `RED`, `GREEN`, and `BLUE` bits.
- During initialization, validates byte mode, 3 components, non-direct input, and absence of white-line callback mode.

Notable dependencies:
- Shared Stylus Color definitions from `gdevstc.h`.

Research notes:
- Like `stc_gsmono`, this is a simple pass-through/packing algorithm rather than an error diffusion routine.
- It relies on the caller to provide valid RGB component ordering.
