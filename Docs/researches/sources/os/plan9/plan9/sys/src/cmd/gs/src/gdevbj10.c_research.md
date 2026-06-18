# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbj10.c

Ghostscript Canon Bubble Jet BJ-10e/BJ-200/BJ-300 family printer driver.

Key behavior:
- Defines `gs_bj200_device` and `gs_bj10e_device`, both monochrome 360 DPI printer devices sharing `bj10e_print_page`.
- `bj200_open` and `bj10e_open` set margins based on A4 vs letter width and model-specific top/bottom constraints, then open the printer.
- `bj10e_print_page`:
  - Allocates input scanline and transposed output buffers.
  - Sends BJ initialization commands, disables automatic carriage return, sets vertical spacing, and sets printable page length.
  - Scans for blank lines and emits vertical skip commands.
  - Transposes raster data in 8-line blocks into printer head-column format using `gdev_prn_transpose_8x8`.
  - Aligns the last pass so the print head does not move below the bottom printable margin.
  - Coalesces blank and non-blank horizontal column groups, emits horizontal skip/data commands, and sends form feed at page end.

Notable dependencies:
- Uses only the Ghostscript printer device API from `gdevprn.h`.

Research notes:
- The long comments document hardware DIP-switch behavior, paper-size assumptions, and BJ-300 Proprinter-mode use.
- `USE_FACTORY_DEFAULTS` changes reset behavior for letter vs A4 paper, but is disabled by default because factory defaults may differ by market/model.
- The code carefully models physical head constraints: 64 jets exist but only 48 are used per strip, which affects effective bottom margin.
- Memory cleanup is centralized through `fin`, so allocation and scanline errors release buffers before returning.
