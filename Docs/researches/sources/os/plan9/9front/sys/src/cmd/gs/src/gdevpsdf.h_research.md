# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsdf.h

## Purpose
Shared header for PostScript and PDF writer devices. It defines common distiller parameters, psdf device state, image parameter structures, binary writer APIs, vector output procedure declarations, color-setting helpers, and stream filter setup entry points.

## Main Types
- `psdf_image_params`: controls sampled-image filtering, downsampling, antialiasing, depth, resolution, dictionaries, and filter templates.
- `psdf_distiller_params`: large Distiller-style parameter set covering page encoding, compression, color conversion, image processing, and font embedding.
- `psdf_version`: logical PostScript/PDF language/version levels.
- `gx_device_psdf`: common vector-device base for ps/pdf writers.
- `psdf_binary_writer`: wrapper around stream filter chains for binary/encoded image data.
- `psdf_set_color_commands_t`: command names for fill/stroke color output.

## Key Exports
- Parameter APIs: `gdev_psdf_get_params`, `gdev_psdf_put_params`.
- Vector output helpers: line width/cap/join/miter/dash/flat/logop and path primitives.
- Binary/image helpers:
  - `psdf_begin_binary`,
  - `psdf_encode_binary`,
  - `psdf_CFE_binary`,
  - `psdf_DCT_filter`,
  - `psdf_setup_image_filters`,
  - `psdf_setup_lossless_filters`,
  - compression chooser and image color filters.
- Color helpers:
  - `psdf_adjust_color_index`,
  - `psdf_set_color`,
  - `psdf_round`.
- Stubs for unsupported `get_bits` operations and overprint compositor interception.

## Dependencies
Includes vector device headers, parameter handling, stream implementation headers, ASCII85, CCITT Fax, and psdf stream support.

## Research Notes
This header is the central contract connecting concrete writers such as `gdevps.c` to shared psdf utilities in `gdevpsdu.c`, image filters in `gdevpsdi.c`, parameter handling in `gdevpsdp.c`, and stream implementations in `gdevpsds.c`.
