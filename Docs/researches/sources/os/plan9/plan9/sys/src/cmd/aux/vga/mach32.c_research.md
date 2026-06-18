# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/mach32.c

Controller backend for ATI Mach32.

Core behavior:
- Uses ATI extended indexed registers at assumed default port `0x1CE`.
- Unlocks multiple ATI extended register lock bits.
- Saves extended ATI registers and Mach32 I/O registers.
- Determines memory size from `Misc`.
- Uses a conservative fixed clock table intended to work across unknown clock generator variants.
- Supports 8-bit packed mode setup and legacy aperture access.
- Disables linear aperture/memory boundary in `load()` to keep VGA aperture access usable.
- Programs clock index bits and interlace flag.

Ctlr:
- `mach32`

Notable risks:
- Header states no accelerator support and practical modes only up to 1024x768.
- Clock generator cannot be detected; only a small safe clock subset is available.
- `vga->private = alloc(sizeof(mach32))` allocates pointer-size rather than `sizeof(Mach32)`, which appears to be a real bug.
