# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevps.c

## Purpose
Implements Ghostscript’s PostScript-writing vector devices: `pswrite` and `epswrite`. It converts graphics operations into compact PostScript/EPS output, including page/file structure, path operators, color setting, bitmap/image emission, image caching, and high-level image handling.

## Main Structures And Devices
- `gx_device_pswrite`: extends `gx_device_psdf_common` with `gx_device_pswrite_common_t`, page state, an image binary writer, a fixed-size image cache, deferred page fill tracking, and compact path state.
- `gs_pswrite_device`: normal PostScript writer.
- `gs_epswrite_device`: EPS writer with `ProduceEPS` enabled.
- `psw_path_state_t`: tracks compact polygon/path emission.
- `psw_image_params_t`: stores cached bitmap id, width, and height.

## Key Behavior
- Defines PostScript ProcSet snippets for compact operators such as color setting, path construction, rectangle fills, image masks, ASCII85/hex data, CCITT Fax, and image/colorimage wrappers.
- Opens output through vector-device file handling and emits headers via `psw_begin_file`.
- Writes page headers/trailers, supports separate page output filenames, and finalizes bounding boxes.
- Defers initial erasepage-like rectangle fills until real content begins, avoiding incorrect transfer-function behavior.
- Emits compact path syntax:
  - rounds coordinates to two decimals,
  - compresses polygon line runs,
  - handles closepath/fill/stroke/clip combinations,
  - flushes path data before exceeding operand stack assumptions.
- Supports `copy_mono`, `copy_color`, `fill_mask`, `fill_path`, and `stroke_path`.
- Handles images through both simple bitmap writers and high-level image enumeration:
  - supports image masks, DeviceGray/RGB/CMYK, and some Indexed color spaces,
  - falls back to default raster handling for unsupported cases,
  - buffers binary high-level images to produce DSC `%%BeginData` sizes.

## Dependencies
Uses the psdf common layer from `gdevpsdf.h`/`gdevpsdu.c`, vector device services, Ghostscript stream filters, ASCII85/hex encoders, CCITT Fax, bbox devices, and PostScript header helpers from `gdevpsu.h`.

## Research Notes
This file is the concrete PostScript output device front end. Most shared distiller parameters, binary stream setup, and image filters are delegated to the psdf utility files in this group.
