# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vision864.c

Implements S3 Vision864 controller support.

Key responsibilities:
- Delegates base snarf/init/load/dump to `s3generic`.
- Advertises linear, 2x8, enhanced-mode capabilities.
- Rejects depths above 8 bpp.
- Applies VL-bus adjustments when detected through CRT `0x36`.
- Programs display memory access registers, fetch start, and blank/skew delays.
- Chooses CRT `0x54` values heuristically by horizontal resolution.
- Writes S3 advanced-function register for enhanced mode.

Important interfaces:
- Exports `Ctlr vision864`.
- Uses mode attributes `delaybl` and `delaysc`.

Notes:
- Comments state this is close to 86C801/805 and “needs tuning”.
