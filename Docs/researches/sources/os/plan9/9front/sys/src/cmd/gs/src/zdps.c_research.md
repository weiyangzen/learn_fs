# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zdps.c

Implements general Display PostScript extensions.

Key behavior:
- Provides screen-phase operators `.setscreenphase` and `.currentscreenphase`.
- Implements `.image2`, a device-source image operator using a source gstate, origin, dimensions, image matrix, pixel-copy flag, and optional `UnpaintedPath`.
- Exposes view clipping operators: `viewclip`, `eoviewclip`, `initviewclip`, and `viewclippath`.
- Implements `defineusername`, maintaining the DPS user-name array in stable local VM so it survives save/restore.
- Expands the user-name array geometrically while preserving existing name entries.

Dependencies:
- Uses DPS graphics state APIs, ImageType 2 processing, path/userpath creation, allocator name arrays, and dictionary helpers.

Research notes:
- `.image2` can allocate an `UnpaintedPath`, convert it to a user path, and write it back into the input dictionary.
