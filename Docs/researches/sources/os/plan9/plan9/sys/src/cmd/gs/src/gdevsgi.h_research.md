# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevsgi.h

Purpose: Header for SGI raster file constants and the SGI `IMAGE` structure used by `gdevsgi.c`.

Key contents:
- Defines SGI image magic `IMAGIC`, colormap constants, type masks, RLE/verbatim encoding macros, and helper macros for image stream buffering.
- Defines `IMAGE`, containing the on-disk SGI header fields followed by in-core state used by SGI image routines.

Important dependencies:
- Consumed directly by `gdevsgi.c`.

Notable risks / findings:
- `IMAGE` mixes serialized fields and runtime-only fields; `gdevsgi.c` writes `sizeof(IMAGE)` then pads to 512 bytes, so structure layout and host ABI affect the emitted header.
