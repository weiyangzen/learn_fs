# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/draw.h

Draw-format helper header for Antiword/RISC OS image handling.

Important contents:
- Includes `drawftypes.h`.
- Defines JPEG Draw object header/data structures: `draw_jpegstrhdr` and `draw_jpegstr`.
- Defines `draw_imageType` union for treating embedded image object storage as sprite, JPEG, byte, or word pointers.

Role:
- Supplies local typed views over Drawfile image payloads used by the RISC OS output path.
