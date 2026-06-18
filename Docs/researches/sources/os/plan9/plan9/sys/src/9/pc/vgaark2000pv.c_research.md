# File Research: sources/os/plan9/plan9/sys/src/9/pc/vgaark2000pv.c

ARK2000PV bank-switch and hardware cursor support. `ark2000pvpageset()` writes sequencer registers `0x15` and `0x16` for page banking and returns the old page. `ark2000pvpage()` protects this with `scr->devlock`.

Cursor code disables/enables the ARK hardware cursor through sequencer register `0x20`, sets cursor colors in sequencer registers `0x26` through `0x2B`, computes cursor storage in the last video-memory block, writes the cursor image either through linear framebuffer or banked access, and programs position/preset registers `0x21` through `0x2D`.

Exports:
- `VGAdev vgaark2000pvdev` with page hook.
- `VGAcur vgaark2000pvcur` named `"ark2000pvhwgc"`.
