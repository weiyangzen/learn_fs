# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevdbit.c

Default Ghostscript device bitmap-copying implementation.

Key responsibilities:
- Implements fallback bitmap operations for devices that do not provide optimized methods.
- Implements `gx_default_tile_rectangle` through `strip_tile_rectangle`.
- Implements `gx_default_copy_mono` using fill/background plus masked fill.
- Implements `gx_default_copy_color` by grouping same-color runs into filled rectangles.
- Implements `gx_default_copy_alpha` by reading destination pixels, blending with a source color, re-encoding pixels, and copying accumulated scanlines back.
- Implements default `fill_mask` handling with optional clipping and alpha delegation.
- Implements `gx_default_strip_tile_rectangle`, which breaks tiled fills into copy operations across tile repetitions and phase/shift.
- Provides no-op/error implementations for unsupported alpha/ROP operations.
- Provides unaligned copy wrappers for mono, color, and alpha bitmap data.

Important behavior:
- `gx_default_copy_mono` uses `gx_dc_default_fill_masked`; if both zero and one colors are present, it fills the background first.
- `gx_default_copy_color` supports depths below 8 and byte-multiple depths up to 64 via fall-through byte assembly.
- `gx_default_copy_alpha` supports 1-bit via `copy_mono`; 2-bit and 4-bit alpha are blended on a 0-15 scale.
- If a blended color cannot be represented, alpha is moved toward 0 or 1 and blending retried.
- `gx_default_strip_tile_rectangle` temporarily patches `tile_rectangle` to avoid recursion when delegating to a device-specific implementation.
- Tile copying preserves bitmap ids only when a complete tile is copied; partial copies use `gs_no_bitmap_id`.
- Unaligned wrappers adjust data origin and, if raster alignment is incompatible, split the operation line by line.

Dependencies:
- Core Ghostscript graphics/device headers: device procs, memory devices, clipping devices, drawing colors, raster ops, bitmap ids, interrupt checks, and line accumulation macros.

Notable risks:
- These implementations are intentionally slow fallback paths.
- `gx_default_copy_color` relies on fall-through switch behavior for packed byte assembly.
- `gx_default_copy_alpha` can allocate full input/output scanline buffers and requires working `get_bits`, `decode_color`, and `encode_color` device procs.
- The 24-bit unaligned color adjustment has special modular arithmetic that is easy to break.
- Temporarily mutating a device procedure in `gx_default_strip_tile_rectangle` is fragile if device procs are shared or used concurrently.
