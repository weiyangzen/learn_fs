# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscpixel.c

## Role

`gscpixel.c` implements Ghostscript’s DevicePixel color space, which treats the color value as a raw device pixel index.

This is rendering/device color infrastructure, not filesystem code.

## Main Public Interface

- `gs_cspace_init_DevicePixel`

## Core Behavior

The DevicePixel color space is a one-component, base color space. Initialization accepts only depths 1, 2, 4, 8, 16, 24, or 32.

Restriction clamps the pixel value to `[0, (1 << depth) - 1]`.

Concretization casts the paint value to a `frac` carrying the raw pixel value. Remapping masks the value to the current device color depth and stores it as a pure device color.

DevicePixel disables overprint by resetting effective overprint mode and updating state with `retain_any_comps = false`.

Serialization writes the color-space type and pixel depth.

## Dependencies

Uses color-space internals, device color, overprint state, imager/graphics state, and stream serialization.

## Notable Risks

- Comments note “NOT ENOUGH BITS IN float OR frac” for raw pixel values, especially at larger depths.
- `(1L << depth)` is used for max-value calculation; depth 32 may be architecture-sensitive if `long` width or signed shifting assumptions differ.
