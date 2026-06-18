# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxi12bit.c

Purpose: provides unpacking and rendering support for image data with 12-bit samples, expanded into Ghostscript `frac` values.

Unpacking:
- `sample_unpack_12` reads packed 12-bit samples from 3-byte pairs.
- Handles odd `data_x`, full 3-byte groups, and trailing 1- or 2-byte partial data.
- Writes expanded `frac` samples into the destination buffer using `spread`.
- Exposes `sample_unpack_12_proc`.

Strategy:
- `gs_image_class_2_fracs` selects the frac renderer for `bps > 8`.
- Converts mask color ranges from sample values into `frac` values when image masking is active.

Rendering:
- `image_render_frac` handles 1-, 3-, 4-, and arbitrary-component images.
- Reuses runs of identical samples to reduce color remapping and fill calls.
- Checks mask-color transparency.
- Uses fast device color mapping for gray/RGB/CMYK device-color cases, otherwise decodes into `gs_client_color` and calls color-space remap.
- Emits rectangles for portrait images and parallelograms for transformed images.
- Saves `penum->used.x/y` on errors so rendering can resume.

Dependencies:
- Uses image enumerator state, color space remapping, device color mapping, DDA geometry, and fill APIs.

Research notes:
- The file is closely parallel to `gxi16bit.c`, differing mainly in packed 12-bit unpacking and mask conversion assumptions.
