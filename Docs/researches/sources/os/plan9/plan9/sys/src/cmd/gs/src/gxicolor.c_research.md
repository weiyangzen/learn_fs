# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxicolor.c

Purpose: renders color images with 8 or fewer bits per sample after samples have been expanded to byte-wide values.

Strategy:
- `gs_image_class_4_color` always returns `image_render_color`.
- When mask color is active, it scales mask ranges to byte values and precomputes fast mask/test bits for quick rejection.

Rendering:
- `image_render_color` handles RGB, CMYK/RGBA, gray+alpha, CMYK+alpha conversion, and arbitrary DeviceN-like sample counts.
- Uses a small 256-entry clue/cache table for low-bit sample combinations (`spp * bps <= 12`) to avoid repeated color remapping.
- Checks transparency via precomputed mask/test and full range matching when necessary.
- Maps concrete device colors directly when possible; otherwise decodes samples into `gs_client_color` and remaps through the color space.
- Coalesces adjacent identical/equivalent device colors into runs.
- Emits portrait rectangles, landscape rotated rectangles, or parallelograms depending on image posture.
- Updates `penum_orig->used` on errors for resumable rendering.

Dependencies:
- Uses color-space remap APIs, concrete color remap, color map procs, image DDA state, device fill operations, and ROP-aware rectangle fills.

Research notes:
- Alpha handling is limited to specific cases; comments state DeviceN color plus alpha is unsupported.
- Duplicated fill logic appears for normal and final run paths to avoid passing many locals to a helper.
