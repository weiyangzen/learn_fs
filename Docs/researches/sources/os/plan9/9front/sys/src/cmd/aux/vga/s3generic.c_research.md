# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/s3generic.c

Generic S3 GUI accelerator support used by multiple S3 chip-specific controllers. It unlocks and captures S3 extended CRTC registers, computes generic enhanced/linear-aperture state, loads common S3 registers, and dumps/decodes timing values.

Key behavior:
- `snarf` unlocks S3 extended registers with CRTC `0x38/0x39`, reads registers `0x30` through `0x6F`, and derives framebuffer size from CRTC `0x36`.
- `init` decides whether enhanced mode is necessary/usable, rejects unsupported wide 1-bpp modes, sets common S3 extended register values, handles interlace bits, chooses horizontal display size code in `Crt50`, configures a placeholder linear aperture, computes aperture size and `Ulinear` state, and packs high overflow bits into `Crt5D`/`Crt5E`.
- `load` writes common extended registers, programs linear aperture base/size when `Ulinear` is active, and marks the controller loaded.
- `dump` prints extended CRTC ranges and, when not dumping initialized state, decodes horizontal and vertical timing values from S3 overflow registers, including special scaling heuristics for 928/Vision964 and ViRGE variants.

Notable dependencies:
- S3 chip-specific wrappers such as `s3801.c` and `s3928.c`.
- VGA framework helpers `resyncinit`, `vgaxi`, `vgaxo`, `printitem`, and `printreg`.

Research notes:
- The generic controller sets `ctlr->type = s3generic.name`, so chip-specific drivers can share a common type marker.
- Linear aperture setup initially assumes a 64 KiB aperture at VGA memory, then final base/size is resolved before load from `vga->vmb`/`vga->vmz`.
- Timing decode in `dump` is heuristic and partly chip-name-dependent.
