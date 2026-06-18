# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevevga.c

## Role
`gdevevga.c` supplies DOS BIOS support routines for Ghostscript IBM PC EGA/VGA display drivers; rendering code lives elsewhere in `gdevpcfb.c`.

## Entry Points
- `pcfb_set_signals`: no-op because this environment cannot catch signals.
- `pcfb_get_state`: captures BIOS text/display mode, page, cursor mode, font, text attribute, and border color through `int86(0x10, ...)`.
- `pcfb_set_mode`: switches BIOS video mode.
- `pcfb_set_state`: restores captured BIOS display state, including font, cursor, page, and border color.

## Risks and Notes
- DOS/BIOS-specific code using interrupt 0x10.
- No filesystem logic. It manipulates display hardware state through BIOS calls.
