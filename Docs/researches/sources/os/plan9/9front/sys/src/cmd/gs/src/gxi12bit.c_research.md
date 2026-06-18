# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxi12bit.c

## Role

`gxi12bit.c` implements 12-bit image sample unpacking and a high-depth image renderer that works on expanded Ghostscript `frac` samples.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `sample_unpack_12_proc`: exported unpack procedure for packed 12-bit source samples.
- `gs_image_class_2_fracs`: image-class selector that chooses `image_render_frac` for images with `bps > 8`.
- `image_render_frac`: renderer for expanded high-depth samples.

## Important Behavior

- `sample_unpack_12` unpacks two 12-bit samples from each three input bytes, handles odd `data_x`, partial trailing bytes, and writes identity-mapped `frac` values with caller-provided `spread`.
- `gs_image_class_2_fracs` converts mask color values to `frac` range values when mask color is in use.
- `image_render_frac` coalesces consecutive samples that map to the same device color, then fills one rectangle or parallelogram per run.
- Supports 1-component gray, 3-component RGB, 4-component CMYK, and default DeviceN/multi-component paths.
- Supports source color masking by testing high-depth samples against `penum->mask_color`.

## Dependencies And Integration

- Uses image enumerator state from `gximage.h`, color-space remapping, device color mapping, DDA fixed-point stepping, and device fill procedures.
- Uses `bits2frac`, `decode_frac`, RGB/CMYK color map procs, and `gx_fill_rectangle_device_rop`.

## Notable Risks

- The renderer assumes the high-depth samples have already been expanded into `frac` units.
- `bufend` is computed as `psrc + w`, where `w` is documented elsewhere as samples rather than pixels; correctness depends on callers passing a sample count compatible with `spp` stepping.
- The final run is always filled with `fill_parallelogram`, even when earlier portrait runs use rectangle filling; this mirrors the 16-bit file and may be intentional but is worth checking for performance/consistency.
