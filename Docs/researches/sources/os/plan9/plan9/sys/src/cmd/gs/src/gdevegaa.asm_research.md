# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevegaa.asm

16-bit x86 assembly helpers for PC EGA/VGA framebuffer operations.

Key contents:
- `_vesa_call_set_page` calls VESA page-switch procedure.
- Defines `rop_params` layout shared with C framebuffer code.
- Implements `_memsetcol`, `_memsetrect`, `_memrwcol`, `_memrwcol2` for column/rectangle fill and shifted bitmap copy using far pointers.
- Preserves registers expected by Turbo C large memory model.

Risks / notes:
- Architecture- and compiler-model-specific DOS code.
- C and assembly must keep `rop_params` layout exactly aligned.
