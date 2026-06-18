# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxicolor.c

## Role

`gxicolor.c` implements Ghostscript's general color image renderer for images with 8 or fewer bits per sample after unpacking.

This is image rendering infrastructure, not filesystem code.

## Main Interfaces

- `gs_image_class_4_color`: image-class selector for general color rendering.
- `image_render_color`: renderer for color image scan lines.

## Important Behavior

- Initializes optimized mask-color tests by scaling image mask ranges to byte sample space and storing bitmask/test shortcuts.
- Uses a `color_samples` union so up to four byte samples can be compared quickly as a 32-bit key.
- Maintains a small clue/cache table for low-bit-depth colors (`spp * bps <= 12`) to avoid repeated color remapping.
- Coalesces adjacent source samples/runs that produce equal device colors and emits one fill per run.
- Handles portrait, landscape, and skewed images with rectangle or parallelogram fills.
- Supports gray/RGB/CMYK-like component counts, alpha cases for gray+alpha and CMYK+alpha conversion to RGB+alpha, and default DeviceN handling.
- Uses concrete color remapping for device color spaces and general `remap_color` otherwise.

## Dependencies And Integration

- Uses image DDA state, color-space decode/remap procs, color-map procs, device colors, RasterOp logical operations, and device fill methods.
- Uses `gx_image_clue` cache entries from the image enumerator.

## Notable Risks

- The renderer has duplicated fill logic for per-run and final-run paths; changes must be mirrored carefully.
- Cache use is disabled inside the DeviceN path but the comment says this should happen during initialization.
- The alpha path explicitly says DeviceN color plus alpha is unsupported.
- Correctness depends on `mask_color.mask/test/exact` matching the unpacked byte sample representation.
