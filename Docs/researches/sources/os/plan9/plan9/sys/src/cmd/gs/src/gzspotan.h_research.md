# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzspotan.h

Declares the spot analyzer device interface and data structures. The header states the analyzer consumes trapezoid fill output for glyph grid fitting and antialiased rendering, with current implementation focused on vertical stem recognition.

Key types:
- `gx_san_trap`: trapezoid geometry, outline segment pointers, band topology, side flags, and recognizer state.
- `gx_san_trap_contact`: cyclic neighbor relationship between lower and upper trapezoids.
- `gx_san_sect`: emitted stem section with left/right coordinates, outline segment pointers, and side mask.
- `gx_device_spot_analyzer`: Ghostscript device plus trap/contact buffers and current topology state.

Exports analyzer lifecycle, trapezoid storage, and stem generation functions.
