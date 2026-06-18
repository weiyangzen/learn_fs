# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/vga/vesadb.c

Generated VESA DMT timing database for `vesa.c`.

Contents:
- Static `Mode` definitions for 30 standard modes:
  - 640x480 at 60/72/75/85 Hz
  - 800x600 at 56/60/72/75/85 Hz
  - 1024x768 at 60/70/75/85 Hz
  - 1152x864 at 75 Hz
  - 1280x960 at 60/85 Hz
  - 1280x1024 at 60/75/85 Hz
  - 1600x1200 at 60/65/70/75/85 Hz
  - 1792x1344 at 60/75 Hz
  - 1856x1392 at 60/75 Hz
  - 1920x1440 at 60/75 Hz
- Each mode stores active dimensions, horizontal/vertical total, blanking, sync ranges, pixel clock, sync polarity, and interlace flag.
- Exports `Mode *vesamodes[]` null-terminated lookup table.

Use:
- `vesa.c` uses it to resolve EDID established and standard timing names without relying on external `vgadb`.

Filesystem relevance:
- None directly; static display timing data.
