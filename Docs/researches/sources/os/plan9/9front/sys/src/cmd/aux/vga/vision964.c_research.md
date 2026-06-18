# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision964.c

Implements S3 Vision964 controller support.

Key responsibilities:
- Snarfs base S3 state plus CRT registers `0x22`, `0x24`, and `0x26`.
- Advertises linear and enhanced capabilities.
- Rejects depths above 8 bpp.
- Resynchronizes timings for enhanced mode, especially when RAMDAC clock doubling is active.
- Computes SID divide settings from RAMDAC bus width, clock doubling, and bits per pixel.
- Adjusts SAM size, display FIFO, CRT delay, VCLK phase, and enhanced-mode flags.
- Writes enhanced CRT registers and S3 advanced-function register.

Important interfaces:
- Exports `Ctlr vision964`.
- Depends on `s3generic`, RAMDAC capability flags such as `Hsid32` and `Uclk2`, and attributes `sam512`, `vclkphs`, `delaybl`, `delaysc`.

Notes:
- Primarily supports enhanced 8-bit modes with external RAMDAC cooperation.
