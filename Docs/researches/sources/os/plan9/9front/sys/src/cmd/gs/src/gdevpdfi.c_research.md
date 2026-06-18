# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfi.c

Ghostscript `pdfwrite` high-level image handling. It decides when images can be emitted directly to PDF, when they need masks/resources/patterns, and when to fall back to Ghostscript’s default image rendering.

Key behavior:
- Defines `pdf_image_enum`, a Ghostscript image enumerator that tracks image geometry, rows remaining, bits per pixel, transformation matrix, and a `pdf_image_writer`.
- Supports ImageType 1, ImageType 3 masked images, ImageType 3x soft-mask images, and ImageType 4 color-key masked images under PDF compatibility constraints.
- Converts certain 1-bit ImageType 4 color-key images into ImageType 1 imagemasks when RasterOp and colors permit, avoiding PDF color-key-mask problems.
- Falls back to default rendering for unsupported alpha, subrectangles, formats, zero-size images, components over 8 bits, singular matrices, unsupported color spaces, or unsupported compatibility-level combinations.
- Handles named images from the `NI_stack`, keeping the stack synchronized even when image handling falls back.
- Chooses inline images only for default ImageType 1 cases without names and below `MaxInlineImageSize`; otherwise creates XObject image resources.
- Computes PDF image matrices from bitmap coordinates, inverse image matrices, and current CTM.
- Sets up lossless or image-compression filters, optional alternative compression streams, process-color conversion filters, and optional mask extraction streams.
- Writes planar image data by flipping component planes into chunky row data before writing to each active binary stream.
- Finalizes images by completing data, padding incomplete DCT/PNG streams as needed through `gdevpdfj.c`, choosing compression, attaching `/Mask` or `/SMask`, drawing XObjects, or saving mask IDs for later use.
- Implements ImageType 3/3x dummy devices that route mask/data begin-image calls back into `pdf_begin_typed_image`.
- Uses image-as-pattern fallback for old PDF levels when masks and patterns need to simulate unsupported image forms.
- Implements `gdev_pdf_pattern_manage`, including pattern accumulation, Pattern resource deduplication/substitution, resource loading, and resource-cache dropping after many substituted patterns.

Notable dependencies:
- Ghostscript image APIs: `gximage3.h`, `gximag3x.h`, `gsiparm4.h`, `gsflip.h`, and image enum procedures.
- Drawing/color/pattern interfaces from `gdevpdfx.h`, `gdevpdfg.h`, `gdevpdfo.h`, `gxdcolor.h`, `gxpcolor.h`, and `gxhldevc.h`.
- Shared local converter device functions from `gdevpdfd.c` through `pdf_setup_masked_image_converter`, `pdf_dump_converted_image`, and `pdf_remove_masked_image_converter`.

Research notes:
- The file has multiple compatibility branches keyed on PDF 1.2, 1.3, and 1.4: color-key masks require newer PDF unless converted, and soft masks require PDF 1.4.
- The fallback label notes that cleanup is incomplete in some failure paths: “SHOULD FREE STRUCTURES AND CLEAN UP HERE.”
- Image merging/deduplication affects mask handling, so the code delays adding `/Mask` or `/SMask` until final image completion.
- This is image/PDF output infrastructure rather than filesystem code.
