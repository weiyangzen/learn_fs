# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision968.c

Implements S3 Vision968 controller support.

Key responsibilities:
- Snarfs base S3 state plus extended sequencer and CRT ID/control registers.
- Advertises linear and enhanced capabilities.
- Rejects depths above 8 bpp.
- Resynchronizes horizontal timings for RAMDAC clock doubling or enhanced 8-bit mode.
- Computes optional external SID divide settings when RAMDAC supports `Hextsid`.
- Programs enhanced-mode CRT flags, SAM selection, DAC-related clock phase, blank/skew delays, and advanced-function output.

Important interfaces:
- Exports `Ctlr vision968`.
- Depends on `s3generic`, RAMDAC flags `Hextsid`, `Hsid32`, `Uclk2`, and attributes `disa1sc`, `vclkphs`, `delaybl`, `delaysc`.

Notes:
- Contains STB Velocity 64 Video-specific empirical handling around `disa1sc` and CRT `0x67`.
