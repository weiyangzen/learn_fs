# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcif.c

Ghostscript output driver that converts a monochrome page into CIF layout commands.

Key responsibilities:
- Defines the `cif` printer device at configurable `X_DPI`/`Y_DPI`, defaulting to 72 dpi.
- Derives a CIF cell/name from the output filename before the first dot.
- Scans rendered monochrome bits and writes CIF `B` box commands for set pixels or runs of set pixels.
- Emits CIF prologue and epilogue commands around the generated geometry.

Important behavior:
- Default path performs horizontal run coalescing: consecutive set bits in a scanline become one wider CIF box.
- `TILE` compile-time option switches to a simpler per-pixel box emission path.
- Coordinates are scaled by 4 and y is emitted as `pdev->height - lnum`.

Dependencies:
- Ghostscript printer API and scanline copying from `gdevprn.h`.

Notable risks:
- The non-`TILE` path does not flush a run if the scanline ends while `length != 0`, so runs reaching the final bit of the line can be dropped.
- The string allocation uses `length = strlen(fname) + 1`, then writes `s[length] = '\0'`; this allocates one byte too few in the no-dot case.
- The generated CIF naming and geometry are very simple and assume one-bit input.
