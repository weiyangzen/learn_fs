# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdither.h

Interface to DeviceN dithering/halftone helpers implemented in `gxdevndi.c`.

- Includes `gxfrac.h`.
- Forward-declares `gx_device_halftone`.
- Declares `gx_render_device_DeviceN`, which renders an array of fractional DeviceN component values into a device color, possibly using a halftone.
- Declares `gx_devn_reduce_colored_halftone`, which reduces colored halftones with zero or one varying plane to a pure color or binary halftone.

Role: thin API boundary between color rendering code and DeviceN halftoning implementation.
