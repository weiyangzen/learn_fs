# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdevndi.h

This header declares the interface to DeviceN halftoning support in `gxdevndi.c`. It includes `gxfrac.h`, forward-declares `gx_device_halftone`, and declares `gx_render_device_color_devn`.

The declared function accepts fractional red/green/blue/white values, a CMYK flag, alpha, target `gx_device_color`, target device, device halftone, and halftone phase. The comment says it renders a color possibly by halftoning and returns like `gx_render_[device_]gray`.

Note: the C file in this group implements `gx_render_device_DeviceN`, while this header exposes `gx_render_device_color_devn`; the latter is likely implemented elsewhere in the same Ghostscript source tree and delegates into DeviceN rendering.

Filesystem relevance: none. It is a graphics color-rendering interface.
