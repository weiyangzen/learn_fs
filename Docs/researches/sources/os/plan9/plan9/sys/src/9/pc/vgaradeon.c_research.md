# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaradeon.c

ATI Radeon 7xxx/8xxx/9xxx VGA driver. It imports `/sys/src/cmd/aux/vga/radeon.h`, matches PCI IDs from `radeon_pciids`, maps MMIO BAR2, maps the linear framebuffer, and exports `radeonmmio` and `radeonscreen`.

Register helpers provide 8-bit/32-bit MMIO access plus PLL indexed access. Cursor support writes a 64x64 ARGB cursor image near the last megabyte of the framebuffer, programs `CUR_OFFSET`, `CUR_HORZ_VERT_OFF`, `CUR_HORZ_VERT_POSN`, and toggles `CRTC_CUR_EN`.

Blanking:
- `radeonblank()` controls display/hsync/vsync disable bits in `CRTC_EXT_CNTL`.
- It honors `*dpms` values `standby`, `suspend`, and `off`.

Acceleration:
- `radeondrawinit()` supports 8, 15, 16, and 32bpp; disables 3D, flushes/reset the 2D engine, initializes pitch/offset/scissor/datatype/masks, then installs fill and scroll callbacks.
- `radeonfill()` emits solid-color rectangle commands.
- `radeonscroll()` emits source-memory copy commands with direction selected for overlap.
- `radeonwaitfifo()` and `radeonwaitidle()` poll `RBBM_STATUS`.

Overlay hooks are stubs: `radeonovlctl()` unused, `radeonovlwrite()` returns `-1`, and `radeonflush()` does nothing. `HW_ACCEL` is commented, but `radeondrawinit()` still installs acceleration when called by the VGA layer.

Exports `VGAdev vgaradeondev` and `VGAcur vgaradeoncur`.
