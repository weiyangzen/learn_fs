# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbit.c

Ghostscript "plain bits" printer devices used mostly to measure rendering time or dump raw rendered pixels without a real output format.

Key behavior:
- Defines three devices:
  - `bit`: 1-bit monochrome raw bits.
  - `bitrgb`: RGB raw bits.
  - `bitcmyk`: CMYK raw bits.
- Device procedures use normal printer open/output/close, custom color mapping, parameter handling, and a simple `bit_print_page`.
- `bit_print_page` copies each rendered scanline and writes the raw raster bytes directly to `OutputFile`; if the filename is `nul`, it skips writes to measure rendering without I/O.
- `bit_get_params` temporarily restores the real component count, delegates printer parameters, publishes a sample default CRD, and exposes `ForceMono`.
- `bit_put_params` accepts `GrayValues`/`RedValues`/`GreenValues`/`BlueValues` to derive bits per component, supports `ForceMono`, updates `color_info`, closes the device on depth/component changes, and resets CMYK mapping hooks.
- `bit_mono_map_color`, `bit_map_color_rgb`, and `bit_map_cmyk_color` encode/decode gray/RGB/CMYK values across supported depths.

Notable dependencies:
- Ghostscript printer APIs: `gdevprn.h`.
- Parameter/color rendering helpers: `gsparam.h`, `gscrd.h`, `gscrdp.h`, `gdevdcrd.h`, `gxlum.h`.

Research notes:
- The `REAL_NUM_COMPONENTS` macro derives intended component count from the device name character after `bit`, so adding new bit devices requires updating that macro.
- The raw output has no file header, dimensions, or byte-order metadata; it is a diagnostic/rendering benchmark backend rather than an interchange format.
- The depth selection table permits high component depths such as 12 and 16 bits where supported by the color model.
