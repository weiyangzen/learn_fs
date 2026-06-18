# File Research: sources/os/plan9/9front/sys/src/9/pc/vgatvp3026.c

Hardware cursor support for the TI TVP3026 Viewpoint video palette, assumed to be attached to an S3 Vision968 controller.

Key behavior:
- Provides indirect DAC register access through CRTC register `0x55`, similar to the TVP3020 path but with TVP3026-specific direct cursor registers.
- Initializes cursor color table entries and cursor control registers.
- Converts Plan 9 cursor `clr` and `set` bitmaps into the TVP3026 two-plane cursor RAM representation.
- Programs cursor hot spot and low/high X/Y screen coordinates.
- Exports a `VGAcur` implementation for enable, disable, load, and move operations.

Notable dependencies:
- Shared VGA register I/O helpers and cursor definitions.
- S3-specific CRTC control bits for external DAC cursor operation.

Research notes:
- Like `vgatvp3020.c`, this is a DAC cursor shim rather than a full graphics device.
- It assumes the surrounding VGA driver has already selected compatible S3 hardware and DAC routing.
