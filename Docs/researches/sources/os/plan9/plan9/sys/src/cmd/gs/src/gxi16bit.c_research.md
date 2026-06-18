# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxi16bit.c

Purpose: provides unpacking and rendering support for image data with 16-bit samples expanded into `frac` values.

Unpacking:
- `sample_unpack_16` reads big-endian 16-bit samples, converts them to `frac`, and stores them with configured `spread`.
- Exposes `sample_unpack_16_proc`.

Rendering:
- `image_render_frac` is structurally the same high-bit-depth renderer used for 12-bit images.
- Handles gray, RGB, CMYK, and DeviceN-like arbitrary sample counts.
- Performs run detection on expanded sample values.
- Supports mask-color transparency.
- Uses direct device color mapping when available, or color-space decode/remap otherwise.
- Fills portrait rectangles or transformed parallelograms.
- Records partial progress in `penum->used` on errors.

Dependencies:
- Uses Ghostscript image, color, device, DDA, and path/clipping infrastructure.

Research notes:
- Unlike `gxi12bit.c`, this file does not define a separate strategy procedure; it supplies the 16-bit unpacker and renderer implementation in the same style.
