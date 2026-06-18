# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbjcl.h

Public interface for the Canon BJC command-generation library.

Key contents:
- Defines capability bits for BJC model command support, including single-character, session, page, resolution, and image capabilities.
- Defines capability masks for known models: 50, 70, 80, 210, 250, 610, 620, 4000, 4100, 4200, 4300, 4550, 4650, 5500, and 7000.
- Provides `BJC_ENUMERATE_OPTIONS(m)` to generate model/capability tables.
- Declares command emitters for CR/FF/LF, initial condition, initialize, print method, media supply, cartridge identification, page margins, raster compression/resolution/skip, CMYK image data, movement, image format, photo image, continuation image, and indexed image.
- Defines enums for print color, media, quality, black density, short print methods, media supply, media type, cartridge commands, raster compression, CMYK image component, image format, and ink system.

Notable dependencies:
- Includes `<stdio.h>` as a patch for `stream.h`, then includes Ghostscript `stream.h`.

Research notes:
- The header documents that the library is preliminary and not every printer supports every command.
- It includes many model-specific notes where numeric enum values mean different things for different printer families.
- The header/source pair is inconsistent for at least initial-condition and compression function names, and the header declares a photo-image function not present in the implementation read in this group.
