# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vision864.c

S3 Vision864 controller support, similar to older 86C801/805 path.

Key behavior:
- Delegates baseline work to `s3generic`.
- Advertises linear, 2x8 pixel clock, and enhanced mode.
- Rejects depths above 8 bpp.
- Sets VLB-related bits for certain bus encodings.
- Programs display memory access registers `Crt60-62`, memory-control `Crt54`, clock-doubler mode bit in `Crt67`, and blanking/skew adjust register `Crt6D`.
- Supports database attributes `delaybl` and `delaysc`.
- Loads additional registers and writes advanced-function control port `0x4AE8`.

Filesystem relevance:
- Indirect display hardware support.
