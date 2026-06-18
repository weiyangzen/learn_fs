# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/png2sprt.c

RISC OS sprite-output stub for PNG images.

Key responsibilities:
- Defines `bTranslatePNG()` for the sprite backend.
- Does not implement PNG-to-sprite conversion.
- Inserts a backend dummy image placeholder instead.

Dependencies:
- Uses `bAddDummyImage()` and Antiword image metadata types.

Notable risks:
- PNG images are intentionally unsupported for this backend, so visual output is a placeholder only.
