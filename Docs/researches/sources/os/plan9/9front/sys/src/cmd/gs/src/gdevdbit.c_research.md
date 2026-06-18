# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdbit.c

Default Ghostscript bitmap-copying implementation for devices that do not provide optimized operations.

Key behavior:
- `gx_default_tile_rectangle` maps tile requests to `strip_tile_rectangle`.
- `gx_default_copy_mono` fills monochrome masks via device colors and `gx_dc_default_fill_masked`.
- `gx_default_copy_color` implements slow row-run rectangle filling for packed color bitmaps, delegating 1-bit depth to `copy_mono`.
- `gx_default_copy_alpha` simulates alpha by reading destination pixels, decoding colors, blending component values, re-encoding, and writing accumulated lines.
- `gx_default_fill_mask` handles optional clipping and alpha/mask dispatch.
- `gx_default_strip_tile_rectangle` tiles a strip bitmap over a rectangle, handling shallow, narrow, and full tiling cases, and avoids recursion if a device’s tile proc conditionally calls the default strip implementation.
- `gx_copy_*_unaligned` wrappers adjust misaligned source pointers/raster strides and fall back to line-by-line copying where needed.
- `gx_no_copy_alpha`, `gx_no_copy_rop`, and `gx_no_strip_copy_rop` are negative stubs returning unknown-error.

Notable dependencies:
- Core Ghostscript graphics/device headers: clipping, rops, device colors, memory devices, bitmap tables, and alignment helpers.

Research notes:
- This is shared rendering fallback infrastructure and is more central than most other files in this group.
- The implementations favor correctness and portability over speed, and comments repeatedly describe them as inefficient defaults.
- The alpha path relies on target device `get_bits`, `decode_color`, and `encode_color`; if a device cannot represent a blended color it adjusts alpha toward representable endpoints.
