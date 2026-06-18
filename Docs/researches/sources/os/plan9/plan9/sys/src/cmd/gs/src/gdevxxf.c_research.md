# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevxxf.c

Read status: complete.

Purpose: implements Ghostscript external font (`xfont`) support for X11 devices. It lets Ghostscript use server-side X fonts for selected PostScript fonts and sizes instead of rasterizing glyphs internally.

Key structures and interfaces:
- Defines `x_xfont`, wrapping `gx_xfont_common`, `gx_device_X *`, `XFontStruct *`, encoding index, mirror flag, and rotation angle.
- Exposes `gdev_x_get_xfont_procs`, returning an X font procedure table with lookup, glyph mapping, metrics, rendering, and release callbacks.
- Uses Ghostscript GC metadata via `gs_private_st_dev_ptrs1`.

Main logic:
- `find_fontmap` locates a PostScript-to-X11 font mapping in linked `x11fontmap` lists.
- `find_x_font` lists matching X fonts lazily with `XListFonts`, detects exact bitmap sizes, and constructs scalable XLFD names when enabled.
- `x_lookup_font` accepts only axis-aligned or 90-degree rotated matrices, rejects very small or very large fonts, checks font extension/scalable support for rotation, mirroring, or non-square scaling, and loads the X font with `XLoadQueryFont`.
- `x_char_xglyph` maps Ghostscript character codes into X glyph byte codes, including standard/ISO remapping through `gs_map_std_to_iso` and `gs_map_iso_to_std`.
- `x_char_metrics` converts X font metrics into Ghostscript widths and bounding boxes, adjusting the advance vector for rotation.
- `x_render_char` either buffers direct X text drawing for X11 devices or renders through a 1-bit X pixmap, reads back with `XGetImage`, and calls the target device’s `copy_mono`.

Filesystem/storage relevance:
- No filesystem implementation. It is graphics/font runtime code, but it is part of the Ghostscript platform/device layer inside the Plan 9 source tree.

Notable behavior and risks:
- Font use is intentionally bounded to sizes 6 through 35 pixels to avoid poor small-font metrics and expensive large server rasterization.
- 16-bit/two-byte X fonts are rejected.
- `x_release` frees only the Ghostscript wrapper object; X font freeing is disabled because the device may not be open.
- If wrapper allocation fails after `XLoadQueryFont`, the loaded X font is not freed in this file.
