# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcfb.h

This header defines the IBM PC framebuffer interface for the EGA/VGA Ghostscript devices.

It declares device procedures for opening, closing, filling rectangles, tiling, copying mono/color data, and reading scan lines. `pcfb_bios_state` records display mode, text page, cursor mode, font, text attribute, and border color so `gdevpcfb.c` can restore text mode after graphics use. The platform hooks `pcfb_set_signals`, `pcfb_get_state`, `pcfb_set_mode`, and `pcfb_set_state` are declared here.

`gx_device_ega` extends `gx_device_common` with framebuffer raster, segmented-address multipliers, and video mode. The `mk_fb_ptr` macro computes framebuffer addresses either through segmented DOS-style pointers or, on Unix/Linux/SVR4-like builds, through a flat `fb_addr`.

The `ega_device` macro builds device descriptors with screen dimensions, computed DPI, color-component counts, depth, dither levels, raster, addressing multipliers, and video mode. The header also defines VGA/EGA register ports and indices: sequencer map mask, graphics set/reset, function, read plane, mode, bit mask, and frame-buffer base `0xa000`.

For Unix-like builds, the header supplies inline GCC assembly for `outportb` and `outport2`; for DOS, it uses `dos_.h` port I/O. The `byte_discard` macro intentionally reads volatile framebuffer bytes to trigger VGA latch behavior and prevent compiler removal.
