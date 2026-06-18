# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/main.c

Contains the `aux/vga` command entry point and orchestration flow. It parses flags for BIOS string override, dump, init, load, palette, refresh, monitor/db selection, tilt, verbosity, and mode/virtual-size arguments.

The command identifies the controller through `dbctlr` or VESA fallback, snarfs all linked controllers, resolves modes from VESA, monitor database, or EDID, computes default frequency from video/memory bandwidth when needed, runs controller `options` and `init`, assigns a Plan 9 channel string, and optionally dumps state.

For load mode, it validates framebuffer size, sets draw-device type, configures linear aperture, writes draw size, disables the display sequencer around non-VESA register loads, runs each controller `load`, calls `drawinit`, selects hardware or software cursor, writes actual size and tilt, then exits.
