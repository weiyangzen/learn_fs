# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/jpeg2sprt.c

This file translates JPEG images for RISC OS draw/sprite output.

Key routines:
- `bSave2Draw(...)` reads the JPEG bytes into memory and inserts them into the draw diagram with `vImage2Diagram`.
- `bTranslateJPEG(...)` seeks to the JPEG data and either embeds it directly for RISC OS 3.6+ or emits a dummy image for older systems.

Important behavior:
- JPEG support is gated on `iGetRiscOsVersion() >= 360`.
- A disabled debug helper can write JPEGs to the Wimp scrap directory and set filetype.

Dependencies:
- RISC OS version helper, data offset seeking, allocation helpers, diagram image insertion, dummy image renderer.

Role in antiword:
- Provides the RISC OS-specific JPEG image path.
