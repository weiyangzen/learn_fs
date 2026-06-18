# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdm24.c

Ghostscript high-resolution 24-pin dot-matrix printer driver for NEC P6-compatible and Epson LQ850-compatible devices.

Key behavior:
- Defines `necp6` and `lq850` 360x360 DPI monochrome printer devices.
- `dot24_print_page` handles the common raster pipeline for both devices, parameterized by model-specific initialization strings.
- Reads 24 or 48 scanline blocks depending on vertical resolution, interleaves odd/even passes for 360 DPI, and transposes row-major bitmap data into 24-pin column bytes via `memflip8x8`.
- Skips blank rows with vertical movement commands and skips long horizontal zero runs with tab stops where worthwhile.
- Emits ESC/P-style 24-pin graphics runs through `dot24_output_run`.
- `dot24_improve_bitmap` clears selected adjacent pixels at 360 DPI to account for printers that cannot print adjacent dots reliably.
- Model entry points only choose the NEC P6 or LQ850 initialization sequence.

Notable dependencies:
- Ghostscript printer API: `gdevprn.h`.
- Memory bit-transposition helper `memflip8x8`.

Research notes:
- The file is pure printer-output conversion code.
- Allocation failures are handled for both input and output buffers.
- The driver mutates the generated bitmap in `dot24_improve_bitmap` for device-physics compatibility, trading exact raster fidelity for printable output.
