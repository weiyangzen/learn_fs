# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmac.c

Implements the legacy Classic MacOS `macos` Ghostscript PICT output device. The file itself notes this device is superseded by the newer `gsapi_*` interface and DISPLAY device.

Key behavior:
- Defines `gs_mac_procs`, wiring core device operations to Mac-specific open, close, sync, output-page, fill, copy-mono, draw-line, copy-alpha, params, and xfont hooks.
- Defines public `gs_macos_device` with default 72 dpi letter dimensions, PICT handle state, output filename/file state, xfont flags, and font cache state.
- `mac_open` allocates a `PicHandle`, writes a PICT header, fills in page/media dimensions and resolutions, and reports device-open callback events through `pgsdll_callback`.
- `mac_get_initial_matrix` maps Ghostscript coordinates into Mac-style page coordinates with negative y scale.
- `mac_sync_output` writes an end-picture opcode in place and sends a sync callback.
- `mac_output_page` optionally saves a PICT file, sends page callback, and finishes the Ghostscript output page.
- `mac_save_pict` writes the 512-byte PICT file header followed by the generated PICT data.
- `mac_close` unlocks/resizes/disposes the PICT handle depending on output mode and sends the close callback.
- Drawing operations serialize PICT opcodes:
  - `mac_fill_rectangle` writes RGB foreground and `fillRect`.
  - `mac_draw_line` writes RGB foreground and line opcode.
  - `mac_copy_mono` writes a bitmap/PackBits rectangle with foreground/background colors and QuickDraw transfer mode.
  - `mac_copy_alpha` simulates alpha on white background by building a color table that shifts saturation/value toward white.
- `mac_convert_rgb_hsv` and `mac_convert_hsv_rgb` support alpha color-table generation.
- `mac_set_colordepth` supports depths 1, 4, 7, 8, and 24, updating `color_info` and RGB mapping procs.
- `mac_put_params` handles `UseExternalFonts`, `BitsPerPixel`, and `OutputFile`, respecting `LockSafetyParams`.
- `mac_get_params` publishes the same parameters.
- Exports `gsdll_get_pict` to return the generated `PicHandle`.

Dependencies and notes:
- Depends on `gdevmac.h`, `gdevmacpictop.h`, QuickDraw/Classic Mac APIs, and Ghostscript DLL callbacks.
- `copy_color` and strip tiling are present only in disabled experimental `#if 0` blocks.
- PICT memory is managed through `CheckMem` and `ResetPage` macros from `gdevmac.h`.
