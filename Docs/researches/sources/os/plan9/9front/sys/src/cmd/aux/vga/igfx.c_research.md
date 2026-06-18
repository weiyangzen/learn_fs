# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/igfx.c

Implements modern Intel integrated graphics support for G45, Ironlake, Sandy Bridge, Ivy Bridge, and Haswell-style devices. It models DPLLs, transcoders, FDI, panel fitters, planes, cursors, HDMI, DisplayPort, GMBUS, and AUX state in structured register snapshots.

`snarf` identifies Intel PCI IDs, attaches MMIO, captures generation-specific display registers, maps pipes/fitters/DPLLs, and reads EDID over GMBUS for VGA/LVDS or DisplayPort AUX/DPCD for DP/HDMI-style ports. EDID modes are annotated with `display` and sometimes `lcd` attributes for later mode selection.

`init` supports 32 bpp only. It disables legacy VGA and all active pipes/ports, selects the requested display port from mode attributes, computes PLLs, link M/N values, lanes, DDI/DP/HDMI/LVDS controls, plane stride, cursor-off state, and pipe/transcoder timings.

`load` powers panels down, disables ports/pipes, may extend GTT mappings for the requested framebuffer size, programs clock sources and DPLLs, enables pipes, writes plane/cursor state, enables ports, and trains DisplayPort links over AUX. This is the most complete display pipeline implementation in the group.
