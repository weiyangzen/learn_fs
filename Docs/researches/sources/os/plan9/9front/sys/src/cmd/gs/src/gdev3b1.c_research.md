# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdev3b1.c

## Scope

Interactive console-display driver for AT&T 3B1/7300/UnixPC.

## Key Behavior

- Defines a custom `gx_device_att3b1` with a framebuffer, console window fd, line size, page number, and optional performance-disable flags.
- Opens `/dev/tty`, verifies UnixPC window support with `WIOCGETD`, allocates a page-sized monochrome framebuffer, and draws into it.
- Implements rectangle fill and monochrome bitmap copy directly into the framebuffer using word masks, bit reversal, and rotate operations.
- On output, saves the window image, changes terminal/window modes, displays a screen-sized view into the page, and lets the user scroll/navigate with vi keys, arrows, page keys, and window icons.
- Restores terminal state, border flags, soft label text, cursor mode, and saved screen image on exit.

## Dependencies

Uses Ghostscript device APIs plus UnixPC-specific `<sys/window.h>` and `<sys/termio.h>` ioctls.

## Risks And Invariants

- Assumes console window semantics and fixed screen constants such as `WINWIDTH` / `WINHEIGHT`.
- `copy_mono` assumes short-aligned input bitmap data and even raster alignment.
- Output is interactive and blocks for keyboard input per page.
- Window save/restore behavior is documented as unreliable on some 3B1 window-manager states.
