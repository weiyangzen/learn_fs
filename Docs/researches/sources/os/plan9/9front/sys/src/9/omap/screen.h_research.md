# File Research: sources/os/plan9/9front/sys/src/9/omap/screen.h

Display, cursor, and framebuffer interface header for the OMAP screen code.

Key contents:
- Forward declarations for `Cursor`, `OScreen`, `Omap3fb`, and `Settings`.
- External hooks for mouse tracking, screen attach/flush, cursor control, screen size/aperture, blanking, draw image reset, and software cursor routines.
- `Settings` holds width, height, depth, channel, pixel clock, margins, sync widths, and orientation.
- `OScreen` stores current display settings.
- `Omap3fb` describes the active-color framebuffer.

Research notes:
- Shared by `screen.c` and `devdss.c`.
