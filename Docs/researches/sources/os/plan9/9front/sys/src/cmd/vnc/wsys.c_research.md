# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/wsys.c

## Role

`wsys.c` handles viewer-side integration with the local Plan 9 window system: resizing, mouse input, mouse warping, cursor display, and clipboard synchronization.

## Window And Mouse

- `adjustwin()` resizes the local window to fit the remote framebuffer or current screen bounds.
- `resized()` reacquires the draw window, adjusts size when appropriate, and requests a full update.
- `initmouse()` opens the local window mouse file.
- `readmouse()` installs a dot cursor, reads local mouse events, handles resize records, applies autoscale coordinate conversion, sends VNC mouse events, and releases wheel buttons after wheel motion.
- `mousewarp()` writes a local mouse warp request to the mouse file.

## Clipboard

- `tcs()` runs `/bin/tcs` for charset conversion when the configured charset is not UTF-8, falling back to fd duplication or `/bin/cat`.
- `gotsnarf()` tracks `/dev/snarf` qid version.
- `writesnarf()` receives remote cut text and writes local snarf through optional charset conversion.
- `getsnarf()` reads local snarf through optional conversion.
- `checksnarf()` polls once per second and sends `MCCut` when local snarf changes.

## Notable Limitations And Risk Areas

- Clipboard polling is periodic rather than event-driven.
- Charset conversion forks helper processes and uses `waitpid()` afterward.
- Autoscale coordinate conversion uses floating-point ratios and truncation.
- Mouse event parsing depends on fixed Plan 9 event record width.
