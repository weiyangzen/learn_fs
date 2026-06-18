# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fbio.h

## Role

`fbio.h` defines the historical Sun framebuffer ioctl ABI. It covers framebuffer type discovery, pixrect access, colormap operations, attributes, video control, double buffering, hardware cursors, window IDs, monitor/device information, and framebuffer type codes.

## Core Ioctls And Structures

- `struct fbtype` is returned by `FBIOGTYPE` and reports type, height, width, depth, colormap size, and total size.
- Kernel-only `struct fbpixrect` and `FBIOGPIXRECT` expose pixrect state.
- `struct fbinfo` and `FBIOGINFO` provide physical/kernel-mapped framebuffer information for older devices.
- `struct fbcmap` plus 32-bit `fbcmap32` support `FBIOPUTCMAP` and `FBIOGETCMAP`.
- Attribute structures `fbsattr` and `fbgattr` support `FBIOSATTR` and `FBIOGATTR`, including emulation type, device-specific fields, owner, and possible emulations.
- `FBIOSVIDEO`/`FBIOGVIDEO` control video on/off. Other early ioctls include vertical retrace and window-grabber operations.

## Cursor, Window ID, And Device Info

- Defines double-buffering flags, planes (`FBDBL_A`, `FBDBL_B`, `FBDBL_BOTH`, `FBDBL_NONE`), and `struct fbdblinfo`.
- Defines hardware cursor structures `fbcurpos`, `fbcursor`, and 32-bit `fbcursor32`, plus cursor set bits and cursor ioctls.
- Defines window-id allocation/list/double-buffer structures, including 32-bit list variant, and WID ioctls.
- Defines miscellaneous graphics/device structures: `gfxfb_info`, `cg6_info`, `s3_info`, `p9000_info`, `p9100_info`, `wd90c24a2_info`, and `mon_info`.
- Defines indexed colormap structure `fbcmap_i`, 32-bit `fbcmap_i32`, flags `FB_CMAP_BLOCK` and `FB_CMAP_KERNEL`, and indexed colormap ioctls.

## Framebuffer Type ABI

Defines framebuffer type codes from `FBTYPE_NOTYPE` and early Sun mono/color devices through accelerator/video/plasma/cg14 types, ending with `FBTYPE_LASTPLUSONE`.
