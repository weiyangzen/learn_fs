# File Research: sources/os/bsd/netbsd-src/lib/libedit/refresh.h

## Purpose
Private declarations and state for the refresh subsystem.

## Main Declarations
- `el_refresh_t`: tracks refresh cursor coordinates and old/new vertical extents.
- Refresh APIs: `re_putc`, `re_putliteral`, `re_clear_lines`, `re_clear_display`, `re_refresh`, `re_refresh_cursor`, `re_fastaddc`, `re_goto_bottom`.

## Integration
Used by input handling, prompt rendering, signal resize handling, and editor command implementations that request redraws.

## Risks And Notes
`el_refresh_t` is part of `EditLine` state. Its cursor and line-count fields must stay synchronized with display buffers maintained in `refresh.c`.
