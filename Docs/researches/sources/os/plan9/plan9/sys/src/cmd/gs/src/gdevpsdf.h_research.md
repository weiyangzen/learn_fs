# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsdf.h

## Purpose
Defines the common PostScript/PDF “psdf” output interface: distiller parameters, shared vector-device fields, binary/image stream writer APIs, color-setting helpers, and stubs for unsupported bitmap readback.

## Main Definitions
- `psdf_image_params`: per-image-class settings for filter dictionaries, antialiasing, autofiltering, depth, downsampling, encoding, resolution, and selected stream template.
- `psdf_distiller_params`: full Distiller-like parameter block for page compression, image compression, color conversion, font embedding, and related policy controls.
- `psdf_version`: PostScript/PDF capability levels from Level 1 through LanguageLevel 3.
- `gx_device_psdf_common` / `gx_device_psdf`: common vector-device extension used by pswrite/pdfwrite-like devices.
- `psdf_binary_writer`: filter-chain helper for binary or ASCII-encoded image streams.
- `psdf_set_color_commands_t`: command-name bundle for fill/stroke color operators.

## Key Behavior Exposed
- Provides defaults for general distiller parameters, color/gray/mono image parameters, and font-embedding policy.
- Declares get/put parameter entry points implemented by `gdevpsdp.c`.
- Declares vector output helpers for line state, paths, rectangles, logical operations, and color setting.
- Declares binary stream setup, filter insertion, CCITT/DCT setup, image filter pipelines, compression chooser setup, image-to-mask conversion, and image color conversion.
- Declares unsupported `get_bits` / `get_bits_rectangle` stubs and overprint compositor handling.

## Dependencies
Includes vector device APIs, parameter APIs, stream infrastructure, ASCII85, CCITT Fax, and psdf stream helpers.

## Research Notes
This header is the central contract shared by `gdevps.c`, `gdevpsdu.c`, `gdevpsdi.c`, and `gdevpsdp.c`. It intentionally carries many Distiller parameters that are only partially implemented in the surrounding code.
