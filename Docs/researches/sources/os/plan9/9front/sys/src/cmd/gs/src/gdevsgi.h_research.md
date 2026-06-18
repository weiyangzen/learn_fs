# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsgi.h

Private SGI raster image format definitions used by `gdevsgi.c`.

Key contents:
- Defines SGI image magic `IMAGIC` and colormap constants.
- Defines image type masks and helpers for verbatim vs RLE image data.
- Provides macros for extracting bits-per-pixel and constructing RLE/verbatim type values.
- Defines basic RLE buffer and no-op constants.
- Includes legacy `IMAGE` stream convenience macros such as `ierror`, `ifileno`, `getpix`, and `putpix`.
- Defines the `IMAGE` structure containing on-disk SGI header fields plus in-memory state fields for file, buffer, row starts, and row sizes.

Research notes:
- The header is guarded by `gdevsgi_INCLUDED`.
- The comments state the file was derived from SGI `image.h` and placed in the public domain by the author.
- In this codebase, only a subset of the `IMAGE` fields are used by `gdevsgi.c` for output.
