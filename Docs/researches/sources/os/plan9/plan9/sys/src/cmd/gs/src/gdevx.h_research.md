# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevx.h

Shared declarations for the Ghostscript X11 drivers.

Key contents:
- Defines `x_pixel` and includes bbox/color-management declarations.
- Declares resource tables from `gdevxres.c`.
- Defines X11 font mapping structs `x11fontlist` and `x11fontmap`, including GC descriptor macro.
- Defines `gx_device_X`, the central X11 device state structure.
- Device state includes bbox forwarding fields, optional memory buffer, `XImage`, `Display`, `Screen`, visual/colormap/window/GC handles, Ghostview atoms, update coalescing state, backing pixmap, temporary mono pixmap, halftone tile cache, GC cache, colors, resources, font maps, update thresholds, and buffered text state.
- Provides macros for cached GC updates: fill style, function, font, background, and foreground.
- Declares inter-module procedures for events, updates, clearing, open/close, color setup/freeing, params, xfont procs, and copydevice finalization.
- Defines `FAKE_RES` used to distinguish nominal command-line/default resolution.

Notable implementation details:
- `is_buffered` is separate from `target` because bbox wrapping may temporarily clear the target.
- `DRAW_TEXT` depends on GC state remaining valid from the first buffered text item.
- `gx_device_X` embeds `x11_cman_t` from `gdevxcmp.h`, keeping color management logically isolated but physically part of the device.

Filesystem relevance:
- None.
