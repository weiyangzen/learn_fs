# File Research: sources/os/plan9/plan9/sys/src/9/omap/screen.h

Shared OMAP screen, cursor, devdraw, and mouse interface header.

Key contents:
- Forward declarations for `Cursorinfo`, `OScreen`, `Omap3fb`, and `Settings`.
- External declarations for mouse tracking, mouse position, acceleration, screen attach/flush/blank/cursor functions, devdraw hooks, draw lock, and screen image reset helpers.
- Defines `ishwimage(i)` as false for software-only drawing.
- Defines framebuffer maxima and format:
  - `Wid = 1280`
  - `Ht = 1024`
  - `Depth = 16`
  - palette constants and resolution indices.
- Defines `Settings` timing structure, `OScreen` state, and `Omap3fb` framebuffer pixel array.

Role:
- Connects `screen.c`, devdraw, devmouse, and possible DSS control code.
- Establishes the fixed framebuffer dimensions used by `screen.c`.

Notable constraints:
- `Omap3fb` is a statically shaped 1280x1024 16-bit framebuffer regardless of selected mode.
- `screenaperture`, `screensize`, `physgscreenr`, and `swcursorunhide` are declared but not implemented in `screen.c`.
