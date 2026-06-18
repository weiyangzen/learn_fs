# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdfb.c

## Purpose

`gdevpdfb.c` implements low-level bitmap, mask, image, and bitmap-pattern handling for the PDF-writing device. It converts Ghostscript raster operations into PDF inline images, XObject images, character procedures, or tiling patterns.

## Bitmap Image Utilities

`pdf_make_bitmap_image` fills basic `gs_image_t` dimensions and image matrix for a bitmap rectangle. `pdf_copy_mask_data` emits a 1-bit mask image, either inline or as a resource, optionally reversing row order for patterns. It initializes image-mask parameters, chooses inline vs resource based on `MaxInlineImageSize`, sets up lossless filters, copies mask bits through `pdf_copy_mask_bits`, and finalizes the image writer.

`set_image_color` updates PDF fill color and, unless a separate stroke color exists, stroke color as well.

## Monochrome and Mask Copying

`pdf_copy_mono` is the central mono/mask path. It updates clipping if necessary, then handles mask, inverse-mask, solid black/white, and two-color indexed-image cases. Character-like masks with a bitmap ID and zero source X may be cached as embedded font character procedures: the code begins a char proc, emits image data into it, ends it, and later invokes it with the correct image matrix. Other masks/images are emitted as inline images or XObjects using PDF image writer helpers.

The public `gdev_pdf_copy_mono` validates dimensions and delegates to `pdf_copy_mono` without a clip path.

## Color Bitmap Copying

`pdf_copy_color_data` emits color raster data with a Device color space derived from current device depth. It chooses row order and inline/resource behavior according to pattern mode and byte count, checks for reusable XObject resources by Ghostscript bitmap ID, sets up color-space objects and filters, copies chunky color bytes with `pdf_copy_color_bits`, and finalizes the writer.

`gdev_pdf_copy_color` opens a page stream, clears clipping, calls `pdf_copy_color_data`, and either returns for inline output or invokes the resulting XObject with `pdf_do_image`.

## Masks and Tiling Patterns

`gdev_pdf_fill_mask` optimizes 1-bit pure-color masks by routing them to `pdf_copy_mono`; complex depths or non-pure/non-pattern colors fall back to the default fill-mask implementation.

`gdev_pdf_strip_tile_rectangle` attempts to convert suitable strip-tile fills into PDF tiling Pattern resources. It requires stable tile IDs, zero shift, sufficiently large fill area, and no non-transparent background color. It distinguishes uncolored mask patterns from colored image patterns, creates an image XObject or inline image inside the Pattern stream, works around Acrobat printing bugs by using `/BBox[0 0 1 1]` and resetting CTM during fill, then paints the requested rectangle with the Pattern color space. Unsupported cases fall back to `gx_default_strip_tile_rectangle`.

## Dependencies

The file depends on PDF device internals (`gdevpdfx.h`, `gdevpdfg.h`, `gdevpdfo.h`), color spaces, drawing colors, pattern colors, high-level device colors, PDF image writer/filter helpers, and COS/resource helpers.

## Filesystem Relevance

No direct filesystem behavior is implemented. Output is written through the PDF device's streams.

## Risks and Notes

The code has many mode-dependent return conventions from `pdf_end_write_image`: error, inline-complete, or resource-created. Pattern optimization contains Acrobat-specific constraints such as rejecting image patterns above roughly 64 KB of image data. Character bitmap caching depends on bitmap IDs and text-processing state; incorrect IDs could over-reuse resources.
