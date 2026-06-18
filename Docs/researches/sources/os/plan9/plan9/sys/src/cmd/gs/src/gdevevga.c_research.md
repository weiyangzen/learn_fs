# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevevga.c

DOS BIOS support routines for IBM PC EGA/VGA display drivers.

Key behavior:
- Real rendering is in `gdevpcfb.c`.
- Provides no-op signal setup.
- Saves current BIOS video/text state via interrupt `0x10`.
- Sets/restores display mode, text page, font, cursor mode, text attributes, and border color.

Risks / notes:
- DOS BIOS-only code, not portable.
- Falls back to mode 3 defaults if current mode is not text mode 3.
