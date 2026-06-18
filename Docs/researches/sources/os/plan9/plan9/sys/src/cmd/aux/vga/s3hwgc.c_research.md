# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/s3hwgc.c

Hardware graphics cursor controller declarations for several RAMDAC/S3 combinations.

Key behavior:
- `s3hwgc` init/load checks whether enhanced mode and at least 8 bpp are available; otherwise sets global `cflag` to fall back away from hardware cursor.
- Requests `Uenhanced` through `resyncinit()` when possible.
- Defines placeholder cursor controllers:
  - `bt485hwgc`
  - `rgb524hwgc`
  - `tvp3020hwgc`
  - `tvp3026hwgc`

Important details:
- Placeholder RAMDAC cursor controllers have no callbacks.
- This file coordinates cursor feasibility more than actual cursor image programming.

Filesystem relevance:
- Indirect display utility code.
