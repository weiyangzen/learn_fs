# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpixel.c

## Purpose
Defines the internal `DevicePixel` color space, where the color value directly represents a device pixel.

## Key Behavior
- Defines the `DevicePixel` color-space type.
- `gs_cspace_init_DevicePixel` accepts depths 1, 2, 4, 8, 16, 24, and 32.
- Restricts pixel values to `[0, (1 << depth) - 1]`.
- Concretizes by storing the pixel value in `pconc[0]`.
- Remaps concrete pixel color directly with `color_set_pure`.
- Disables overprint for DevicePixel.
- Serializes the color-space type and depth.

## Important Details
- Comments warn there are not enough bits in `float` or `frac` for fully general DevicePixel values.
- Remapping masks the concrete value to the current device depth.

## Dependencies
Uses color-space internals, device color helpers, overprint state update, imager state, and stream serialization.

## Research Notes
This is a low-level escape hatch for direct device-pixel colors.
