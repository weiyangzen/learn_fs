# File Research: sources/os/plan9/9front/sys/src/9/pc/vga.c

## Role

Low-level Plan 9 PC VGA screen-console support. It initializes the framebuffer console image, writes kernel text to the active screen, handles scrolling, blanking, and exposes framebuffer segments for mapping.

## Main Interfaces

- `vgaimageinit(ulong chan)`: initializes the `Memimage` backing the VGA console.
- `vgascreenputs(char *s, int n)`: console text output entry point.
- `vgascreenwin(VGAscr *scr)`: updates the visible window rectangle for the active screen.
- `vgablank(VGAscr *scr, int blank)`: invokes a driver blank hook when present.
- `addvgaseg(char *name, ulong pa, ulong len)`: publishes physical framebuffer/MMIO regions as image segments.

## Key Behavior

- Creates black and white `Memimage` color tiles and binds the kernel screen image to `gscreen`.
- `vgascreenputc()` interprets newline, tab, backspace, carriage return, and ordinary UTF text rendering using `memimagestring`.
- Scrolls by copying the existing text area upward and clearing the final line when the cursor reaches the bottom.
- `vgascreenputs()` serializes drawing with `screenlock`, decodes runes, writes text, flushes the changed rectangle, and falls back to serial output when the screen is unavailable.
- `vgascreenwin()` computes the logical visible rectangle from configured screen width, actual size, and tilt settings.
- `addvgaseg()` records named physical display regions in the global image segment table.

## Dependencies And Assumptions

- Depends on Plan 9 draw/memdraw types, `VGAscr`, global `vgascreen[0]`, screen locks, cursor hooks, and flush callbacks.
- Assumes a single primary VGA screen for console output.
- `vgablank()` is a dispatcher; real blanking logic lives in chipset-specific VGA drivers.

## Research Notes

- This file is the bridge between kernel text output and the graphics driver modules in the rest of this group.
- It is not a filesystem implementation, but exposed framebuffer segments and `devvga` control files depend on this screen state.
