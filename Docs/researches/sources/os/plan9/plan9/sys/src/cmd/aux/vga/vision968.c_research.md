# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision968.c

S3 Vision968 controller support.

Key behavior:
- Snarfs generic S3 state, sequencer `0x09/0x0A`, CRTC `0x22/0x24/0x26`, and CRTC ID `0x2D-0x2F`.
- Advertises linear and enhanced mode.
- Rejects depths above 8 bpp.
- Like Vision964, handles RAMDAC clock-doubled timing by halving horizontal values and forcing enhanced mode.
- Configures SID divisor only when RAMDAC advertises external SID.
- Sets control bits for enhanced operation, SAM, display skew, optional `disa1sc`, `vclkphs`, `delaybl`, and `delaysc`.
- Special-cases non-TVP3026 RAMDAC behavior for `Crt67`.
- Loads extra registers and advanced-function control.
- Dumps S3 generic plus Vision968-specific sequencer/CRTC registers.

Filesystem relevance:
- Indirect display controller support.
