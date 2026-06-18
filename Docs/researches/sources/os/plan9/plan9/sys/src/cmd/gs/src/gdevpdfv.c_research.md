# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfv.c

## Purpose

`gdevpdfv.c` writes color-related high-level PDF constructs for pdfwrite, especially PatternType 1 tiling patterns, PatternType 2 shading patterns, mesh shading streams, and named color-space inclusion.

This is PDF graphics output code, not filesystem code.

## PatternType 1 Tiling Patterns

- `pdf_pattern` creates a `/Pattern` resource as a stream that paints an image XObject:
  - validates Acrobat image-pattern size constraints,
  - checks that pattern steps align with coordinate axes,
  - creates a resource dictionary containing the image XObject,
  - writes `/PatternType 1`, `/PaintType`, `/TilingType`, `/Resources`, `/BBox`, `/Matrix`, `/XStep`, and `/YStep`,
  - writes `/R<image-id> Do` as pattern stream contents.
- `pdf_store_pattern1_params` stores pattern dictionary fields for high-level pattern streams and sets up `pdev->substream_Resources`.
- `pdf_set_pattern_image` initializes image matrix/size from tile dimensions.
- `pdf_put_pattern_mask` writes a 1-bit mask image for pattern masks, inverting Y because pattern masks are device-coordinate based.

## Colored and Uncolored Pattern Output

- `pdf_put_uncolored_pattern`:
  - can optimize an all-ones uncolored pattern into a pure color when pattern streams are unavailable.
  - otherwise creates or locates a pattern resource and emits the Pattern color space selection.
  - includes an Acrobat Reader 4 stack workaround for some uncolored pattern stream cases.
- `pdf_put_colored_pattern`:
  - detects masked pure-color cases and delegates to `pdf_put_uncolored_pattern`.
  - rejects masked colored patterns for PDF versions before 1.3.
  - writes image and optional mask XObjects, attaches `/Mask`, creates the pattern, or finds a high-level pattern resource.
  - emits colored Pattern color-space selection.

## PatternType 2 and Shadings

- `pdf_put_shading_common` writes shared shading dictionary keys:
  - `/ShadingType`
  - optional `/AntiAlias`
  - `/ColorSpace`
  - optional `/Background`
  - optional `/BBox`
- `pdf_put_shading_Function` writes optional `/Function` using `pdf_function_scaled`.
- `pdf_put_linear_shading` writes `/Coords`, optional `/Domain`, optional `/Function`, and optional `/Extend`.
- `pdf_put_scalar_shading` handles Function-based, Axial, and Radial shadings.
- `pdf_put_mesh_shading` handles mesh shading stream parameters and data:
  - Free-form Gouraud triangle
  - Lattice-form Gouraud triangle
  - Coons patch
  - Tensor-product patch
- `put_float_mesh_data` converts array-backed floating-point mesh data into packed binary with fixed bit widths.
- `pdf_put_pattern2` creates a Pattern resource plus Shading resource, writes scalar or mesh shading representation, computes the pattern matrix in default user coordinates, and emits the Pattern color-space selection.

## Mesh Encoding Details

- Coordinates are limited to a 14-bit-safe Acrobat-compatible range and encoded into 24-bit coordinate fields.
- Color components are encoded into 16-bit component fields.
- Flags are encoded as 8-bit fields for array-backed mesh data.
- For stream-backed mesh data, existing stream contents and decode parameters are copied rather than repacked.

## Other API

- `gdev_pdf_include_color_space` includes a named color-space resource through `pdf_color_space_named`.

## Dependencies and State

- Uses Ghostscript color, pattern, image, shading, and matrix types.
- Depends heavily on image writer helpers from other pdfwrite files, COS helpers from `gdevpdfo`, color-space helpers from `gdevpdfg`, and function writing from `gdevpdfu`.
- Updates PDF resources of types Pattern and Shading, current stream output, and some pdfwrite compatibility flags.

## Risks and Limitations

- Null patterns are explicitly not handled.
- Image patterns are rejected if image/mask data exceeds about 64 KiB due to Acrobat Reader limitations.
- Pattern steps must be axis-aligned; non-axis-aligned steps return `rangecheck`.
- Comments note unscaled `/Background` and `/Decode` cases.
- Mesh packing uses fixed ranges and clamping, so out-of-range geometry/color data is saturated.
- High-level pattern stream resource lookup assumes matching IDs and may return substituted pattern resources.
