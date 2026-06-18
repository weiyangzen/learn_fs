# File Research: sources/os/plan9/plan9/sys/src/cmd/getmap.c

This utility reads or synthesizes an 8-bit display colormap and writes it to `/dev/draw/<id>/colormap`. It supports named map files, `/lib/cmap/`, screen/display/vga aliases, and generated `gamma`/`rgamma` maps.

`getcmap` loads 256 RGB rows or generates gamma-corrected grayscale entries. `putcmap` writes the full colormap table. `main` opens `/dev/draw/new`, verifies an `m8` display, resolves the selected map, and installs it.

The helper `rep` replicates an n-bit value through a `ulong`, though it is not used by `main`.
