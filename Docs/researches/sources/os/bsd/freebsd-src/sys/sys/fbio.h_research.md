# File Research: sources/os/bsd/freebsd-src/sys/sys/fbio.h

## Purpose
Defines framebuffer and video adapter ioctls, data structures, modes, and kernel framebuffer registration hooks.

## Main Interfaces
- Framebuffer type constants `FBTYPE_*`.
- `struct fbtype` and `FBIOGTYPE`.
- RGB offsets: `struct fb_rgboffs`, `FBIO_GETRGBOFFS`.
- Kernel `struct fb_info` with device pointers, enter/leave/blank callbacks, physical/virtual framebuffer addresses, flags, stride, bpp, cmap, RGB offsets.
- Kernel APIs: `fbd_list`, `fbd_register`, `fbd_unregister`, `register_framebuffer`, `unregister_framebuffer`.
- Color map: `struct fbcmap`, `FBIOPUTCMAP`, `FBIOGETCMAP`.
- Video mode and adapter structures:
  - `struct video_info`
  - `struct video_adapter`
  - `struct video_adapter_info`
- Mode constants for legacy VGA/EGA/CGA/Hercules/text/VESA modes.
- Ioctls for adapter info, mode query/set, window origin, display start, line width, palette, blanking, and RGB offsets.

## Dependencies And Integration
Includes `ioccom.h`; kernel builds include eventhandler support so framebuffer registration emits `register_framebuffer` and `unregister_framebuffer` events.

## Risk Notes
All ioctl numbers and structure layouts are ABI. `struct fb_info` embeds a raw `fbtype` prefix that must not be reordered. Some helper macros assume nonzero height and valid bpp/stride fields.
