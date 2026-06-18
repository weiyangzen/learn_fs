# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxi16bit.c

## Role

`gxi16bit.c` implements 16-bit image sample unpacking and a high-depth image renderer that works on expanded Ghostscript `frac` samples.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `sample_unpack_16_proc`: exported unpack procedure for 16-bit big-endian source samples.
- `image_render_frac`: local renderer for expanded high-depth samples.

## Important Behavior

- `sample_unpack_16` reads two bytes per sample, converts to a `frac` with `(frac_1 * (sample + 1)) >> 16`, writes with caller-provided `spread`, and resets `pdata_x`.
- Rendering logic parallels `gxi12bit.c`: detect runs of identical samples/device colors, process mask colors, use concrete RGB/CMYK mapping when possible, otherwise decode and remap through the color space.
- Supports gray, RGB, CMYK, and DeviceN/multi-component paths.
- Saves `penum->used.x` on render error so interrupted image rendering can resume.

## Dependencies And Integration

- Uses Ghostscript fixed-point DDA image state, color remapping, device color mapping, and device fill APIs.
- Includes the same broad image/color/device headers as `gxi12bit.c`.

## Notable Risks

- The unpack loop condition is `while (left > 2)`, which skips exactly two remaining bytes; given two bytes are one complete 16-bit sample, this deserves scrutiny if the caller can pass exact sample-sized buffers.
- The file does not declare an image-class selector like `gs_image_class_2_fracs`; it relies on another compilation unit or class table to route 16-bit expanded data to this renderer/unpacker.
- Like `gxi12bit.c`, the final run uses `fill_parallelogram` even when portrait runs used rectangle filling.
