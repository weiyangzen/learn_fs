# File Research: sources/os/plan9/9front/sys/src/cmd/aux/vga/vesadb.c

Provides built-in VESA DMT monitor timing definitions.

Key responsibilities:
- Defines static `Mode` records for common VESA DMT resolutions and refresh rates.
- Covers modes from 640x480 through 1920x1440, with horizontal/vertical totals, blanking, sync ranges, pixel clocks, and sync polarity.
- Exposes `Mode *vesamodes[]` as a null-terminated timing database.

Important interfaces:
- Used by `vesa.c` to populate timing fields for VBE modes when a matching resolution is found.
- Declared in `vga.h` as `extern Mode *vesamodes[]`.

Notes:
- The comments cite VESA Monitor Timing Standard DMT v1r08 and explain this database allows operation without `vgadb`.
