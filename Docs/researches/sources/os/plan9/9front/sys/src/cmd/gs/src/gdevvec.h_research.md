# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevvec.h

## Purpose
Central shared header for Ghostscript vector-style output devices.

## Main Contents
- Documents vector devices as high-level command streams rather than raster-only devices.
- Defines `gx_path_type_t` flags for fill, stroke, clip, winding/even-odd rules, path optimization, and forced closepath emission.
- Defines `gx_device_vector_procs`, the callback table concrete vector devices implement for page start, graphics-state changes, high-level colors, paths, rectangles, and path segments.
- Defines `gx_device_vector_common`, extending a Ghostscript device with:
  - output file and stream fields,
  - cached imager state and dash pattern,
  - saved fill/stroke high-level colors,
  - clipping path IDs,
  - fill/stroke options,
  - coordinate scale,
  - page mark state,
  - optional bbox device,
  - cached black/white color indexes.
- Declares GC descriptor macros for vector devices and image enumerators.
- Defines output-file option flags for ASCII, sequential, sequential fallback, and bbox tracking.
- Declares utility APIs implemented in `gdevvec.c`.
- Declares default vector device procedures for fills, strokes, and geometric fills.

## Dependencies
Includes Ghostscript platform, RasterOp, device, bbox, image parameter, imager-state, high-level color, and stream headers.

## Notable Risks
The header is a private subsystem contract; concrete vector devices depend on field layout and callback semantics. Several callbacks are optional but utility functions call specific callbacks when advertised behavior requires them.

## Filesystem Relevance
Declares output-file/stream support for vector formats. It is not filesystem implementation code.
