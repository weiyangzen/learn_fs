# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdevndi.h

Public internal interface to DeviceN halftone handling.

- Includes `gxfrac.h`.
- Forward-declares `gx_device_halftone`.
- Declares `gx_render_device_color_devn`, which renders a color possibly by halftoning.
- Signature includes RGB, white, CMYK flag, alpha, output device color, target device, device halftone, and halftone phase.

Note: this header’s declared function name differs from `gxdither.h`’s `gx_render_device_DeviceN`; this file appears to expose a higher-level DeviceN color rendering entry.
