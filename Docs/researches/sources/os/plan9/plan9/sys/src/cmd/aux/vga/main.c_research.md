# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/main.c

This is the main program for `aux/vga`, orchestrating VGA controller detection, mode lookup, register initialization, loading, and draw-device setup.

Key behavior:
- Parses flags for BIOS id, controller dump, software cursor, init, load, print, refresh, verbosity, monitor type, and alternate vgadb path.
- Reads `$vgactlr` and `$monitor`, falls back through vgadb controller probing, VESA probing, then generic VGA.
- Runs every controller’s `snarf`, `options`, `init`, `load`, and `dump` hooks through the linked controller chain.
- Resolves monitor modes from `/lib/vgadb`, `/env/<monitor>`, or VESA mode data.
- Handles physical and virtual screen sizes, including panning setup.
- Chooses default draw channel strings for common depths.
- Computes a mode frequency from video bandwidth and memory bandwidth when only bandwidth constraints are supplied.
- Configures kernel video state through `vgactlw("type")`, `linear`, `size`, `drawinit`, `hwgc`, `actualsize`, and `panning`.

Important details:
- `sequencer()` blanks/unblanks VGA output around hardware register programming.
- `linear()` negotiates and reads back the linear framebuffer aperture from `#v/vgactl`, supporting both old and newer `addr p ... size ...` formats.
- VESA loading is done before linear setup, then the type is switched back for acceleration.
- `rflag` protects refresh-only loads by checking the existing size unless explicitly overridden.
- A zero-byte write to `/dev/cursor` initializes cursor state after mode load.

Filesystem relevance:
- Directly controls Plan 9 device files and namespaces: `/lib/vgadb`, `/env`, `#v/vgactl`, `/dev/cursor`, and draw-device initialization.
