# File Research: sources/os/plan9/plan9/sys/src/9/omap/devdss.c

Implements the OMAP DSS screen control device `#v/vgactl`.

Key points:
- Provides a two-entry device tree: root directory and `vgactl`.
- `screenopen()` serializes `vgactl` access with `dsslck` and marks `oscreen.open`.
- `screenclose()` clears `oscreen.open` and unlocks.
- `settingswrite()` parses display mode strings for `800x600`, `1024x768`, and `1280x1024`, then updates `OScreen.settings`.
- `getchans()` selects `RGB16` or `RGB24`, defaulting to `RGB16`; note comments that RGB24 cannot work yet with short pixels.
- `screenread()` reports size/depth/frequency and framebuffer address/size.
- `screenwrite()` rejects nonzero offsets, applies new settings, and calls `screeninit()`.

Dependencies and interactions:
- Uses globals from `screen.c`/`screen.h`: `oscreen`, `settings`, `framebuf`, and `screeninit()`.
- DSS clocks and GPIO are configured in `archomap.c`.

Research relevance:
- Small Plan 9 device interface connecting user-visible display configuration to OMAP screen setup.
