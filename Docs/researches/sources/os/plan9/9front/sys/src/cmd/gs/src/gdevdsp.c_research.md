# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdsp.c

## Role
`gdevdsp.c` implements Ghostscript's callback-based `display` device. It renders into a memory device bitmap and exposes lifecycle, resize, update, sync, showpage, allocation, and optional separation-color notifications to an embedding application through `display_callback`.

## Main Structures and Entry Points
- Defines `gs_display_device` as a `gx_device_display`, with `display_procs` implementing open, matrix, sync, output page, close, fill/copy/get-bits, parameter get/put, copy finalization, and spot-equivalent update.
- The `gx_device_display` layout comes from `gdevdsp2.h`: it stores the backing memory device, callback pointer, caller handle, display format flags, bitmap pointer/size, resolution state, DeviceN separation parameters, and equivalent CMYK spot color data.
- GC support is declared via `public_st_device_display()` and enumerates/relocates the backing memory device plus separation-name strings.

## Behavior
- `display_open` allows a disabled open when no callback exists. With a callback, it validates callback size/version and required function pointers, configures color format, calls `display_open`, announces proposed size via `display_presize`, allocates the backing bitmap, then calls `display_size`.
- `display_alloc_bitmap` creates a Ghostscript memory device matching the configured depth, optionally obtains the bitmap buffer from `display_memalloc`, marks the memory device as using foreign bits, opens it, and clears the bitmap to white/zero depending on polarity.
- Drawing operations (`display_fill_rectangle`, `display_copy_mono`, `display_copy_color`) delegate to the memory device and then call `display_update` if provided.
- `display_sync_output` and `display_output_page` first refresh separation mapping callbacks when in separation mode, then call host sync/page callbacks. Successful `display_output_page` finishes Ghostscript page output.
- `display_close` emits `display_preclose`, frees bitmap/memory device resources, then emits `display_close`.
- `display_put_params` handles `DisplayFormat`, `DisplayHandle`, and `DisplayResolution`, while preserving old state and rolling back on errors. Format and handle changes are rejected while open; dimensions can change while open through a presize/free/reallocate/size sequence.

## Color and Format Handling
- Supports native 1/4/8/16-bit formats, gray, RGB, CMYK, and DeviceN-style separation output. It validates depth, row alignment, alpha flags, endianness, and color model combinations in `display_set_color_format`.
- Includes specialized encoders/decoders for black-on-white 1-bit, PC 4-bit palette, a 96-entry native 8-bit RGBK palette, 16-bit 555/565 RGB, BGR24, flexible RGB with unused component placement, 1/8-bit CMYK, and separation color packing into `gx_color_index`.
- Separation mode uses Ghostscript DeviceN helpers for color mapping, component lookup, parameter get/put, and equivalent CMYK spot colors. `display_set_separations` sends component name and CMYK equivalent data to V2 callbacks.
- `display_get_initial_matrix` flips between default top-first and upright/bottom-first orientation based on `DISPLAY_FIRSTROW_MASK`.

## Parameters and API Boundary
- Exposes `DisplayHandle` as a hexadecimal string for pointer-size safety, plus `DisplayFormat` and `DisplayResolution`.
- Accepts `DisplayHandle` as a string in decimal, `10#`, or `16#` syntax; 32-bit builds can also accept the legacy numeric form.
- Client-provided callbacks are trusted after structural validation; callback failures are propagated as Ghostscript errors during open/resize/page operations.

## Risks and Notes
- This is embedding-facing API code, not a filesystem component. Its most relevant resource boundary is host-supplied bitmap allocation/free and access to the raw memory buffer.
- It rejects implemented-but-unsupported alpha-first/alpha-last formats, row alignment smaller than pointer alignment, little-endian CMYK/separation, and invalid callback versions.
- The test harness at the end is inside a large comment and documents expected/known display modes.
