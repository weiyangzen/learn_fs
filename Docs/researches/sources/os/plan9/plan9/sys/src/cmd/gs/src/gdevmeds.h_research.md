# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmeds.h

Small interface header for Ghostscript medium-selection support.

- Defines include guard `gdevmeds_INCLUDED`.
- Includes `gdevprn.h`, so the interface is printer-device-specific.
- Declares `select_medium(gx_device_printer *pdev, const char **available, int default_index)`.
- No implementation, data structures, or macros beyond the public prototype.
- Integration role: lets printer drivers ask shared `gdevmeds.c` logic to choose a medium from an available-medium list with a default fallback.
