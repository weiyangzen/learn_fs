# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3generic.c

Shared S3 SVGA/GUI accelerator support used by many controller-specific files.

Key behavior:
- Unlocks S3 extended CRTC registers and snarfs `Crt30-Crt6F`.
- Derives video memory size from `Crt36`.
- Handles enhanced-mode selection and rejects unsupported non-enhanced 1 bpp wide modes.
- Initializes S3 extended CRTC state:
  - timing overflow bits in `Crt5D/5E`,
  - interlace state,
  - display width encoding,
  - linear aperture registers,
  - mode/control registers.
- Loads extended registers in a controlled order, including optional linear aperture base/size.
- Dumps raw S3 register banks and decodes timing fields when not already initialized.

Important details:
- `ctlr->type` is set to `s3generic.name`.
- Uses `vga->virtx` for pitch-related generic VGA state.
- Dump logic special-cases ViRGE 16 bpp timing scaling.

Filesystem relevance:
- Indirect display chipset framework code.
