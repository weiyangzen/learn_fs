# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdfi.c

Ghostscript `pdfwrite` high-level image handling. It decides whether images can be emitted directly to PDF, need masks/resources/patterns, or must fall back to the default renderer.

Key behavior:
- Defines `pdf_image_enum`, an image enumerator tracking geometry, rows remaining, bits per pixel, placement matrix, and `pdf_image_writer`.
- Supports ImageType 1, ImageType 3 masked images, ImageType 3x soft-mask images, and ImageType 4 color-key masked images within compatibility constraints.
- Converts some 1-bit ImageType 4 color-key images into Type 1 imagemasks when RasterOp/color conditions allow.
- Falls back for unsupported alpha, subrectangles, formats, zero-size images, components over 8 bits, singular matrices, unsupported color spaces, and unsupported PDF versions.
- Handles NI-named images and keeps the `NI_stack` synchronized even when falling back.
- Chooses inline images only for unnamed default Type 1 images below `MaxInlineImageSize`; otherwise emits XObject resources.
- Computes PDF image matrices from bitmap geometry, inverse image matrices, and current CTM.
- Sets up lossless or image-compression filters, optional alternative compression streams, process-color conversion, and mask extraction streams.
- Writes planar data by flipping planes into chunky rows for each active binary stream.
- Finalizes images by completing/padding data, choosing compression, adding `/Mask` or `/SMask`, drawing XObjects, or saving mask IDs for later use.
- Implements dummy devices for ImageType 3/3x mask/data callbacks.
- Uses image-as-pattern fallback for older PDF levels when masks/patterns must simulate unsupported forms.
- Implements `gdev_pdf_pattern_manage` for pattern accumulation, deduplication/substitution, resource loading, and cache dropping after many substitutions.

Research notes:
- Compatibility branches distinguish PDF 1.2, 1.3, and 1.4 behavior for masks and soft masks.
- The fallback path explicitly notes incomplete cleanup in some failure cases.
- Mask handling is delayed to account for image merging/deduplication.
