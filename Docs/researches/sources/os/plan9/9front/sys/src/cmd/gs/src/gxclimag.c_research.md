# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclimag.c

Implements higher-level command-list image operations: mask filling, high-level image command emission, image-data banding, compositor command emission, halftone serialization, and color-mapping state emission.

Key behavior:
- `clist_fill_mask` turns suitable mask fills into cached clist copy commands, with copy-alpha translation for multi-bit masks, per-band clipping/color/RasterOp state, bitmap-cache lookup, and fallback to `gx_default_fill_mask` for unsupported cases.
- Rejects optimized mask handling for nontrivial clipping when complex clipping is disabled, debug fallback, uncached bitmap ids, non-default RasterOp, or non-pure alpha colors.
- Defines `clist_image_enum`, extending the common image enumerator with original image parameters, drawing color, source rectangle, imager/clip state, format, interpolation support pixels, bits-per-plane, image-to-device matrix, color-space metadata, conservative device Y range, prebuilt begin-image command, and dynamic row/color-map state.
- `clist_begin_typed_image` supports a restricted high-level path for ImageType 1 and 4; it falls back for nested images, disabled high-level images, CIE/non-basic color spaces, non-pure CombineWithColor, alpha images, varying plane depths, bad matrices, unsupported transforms, excessive row size, or complex clipping restrictions.
- Builds a serialized begin-image command using the image type table and the image type's `sput` procedure.
- Computes conservative colors-used information, exactly enumerating simple low-bit single-component images when feasible and otherwise assuming all device colors.
- Clears known clist state so CTM, color space, clip, alpha/opacity/shape, blend/overprint/text-knockout, and begin-image state are emitted before image data.
- `clist_image_plane_data` maps source rows to affected page bands, computes exact or conservative source subrectangles per band, writes begin-image commands once per band, and streams interleaved plane data in chunks sized for `cbuf_size`.
- Handles VM-error recovery by writing image-end commands, updating state, and forcing image-related state to be re-emitted after recovery.
- `clist_image_end_image` writes EOD image-data commands into all bands that saw a begin-image command, with local recovery and hard-flush fallback.
- `clist_create_compositor` serializes compositor creation, optionally emits CTM first for PDF 1.4 transparency compositors, and writes the compositor as an all-band extended command.
- `cmd_put_halftone` serializes full device halftones, writing a total-length command and splitting large serialized halftones into extended segment commands.
- `cmd_put_color_mapping` emits changed device halftone, black generation, undercolor removal, and transfer maps while suppressing redundant maps by ID.
- `image_band_box` computes the image-source rectangle intersecting a device band, using a fast axis-aligned inverse transform path and a general parallelogram/image-rectangle intersection path for rotated/skewed cases.
- `check_rect_for_trivial_clip` accepts null clips, clips that include the rectangle, or rectangular clips that intersect the rectangle.

Dependencies:
- Uses image type serialization, color-space helpers, clist writer/path command support, image parameter structures, streams, interpolation constants, compositor serialization, and device-halftone serialization.
- Depends on `gxcldev.h` for command opcodes, band macros, bitmap/cache helpers, and color-mapping declarations.

Research notes:
- The high-level image path is intentionally conservative and optimized for rectangular or near-axis-aligned banding; unsupported cases fall back to lower-level default image decomposition.
- `begin_image_command` has a comment warning that its static size computation is tied to image/matrix serialization internals.
- Halftone segments are not recovered transactionally after partial segment submission; the reader discards partial halftones when a new total-length command appears.
