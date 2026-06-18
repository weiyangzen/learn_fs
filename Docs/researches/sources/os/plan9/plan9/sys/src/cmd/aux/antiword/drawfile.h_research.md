# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/drawfile.h

This header defines RISC OS Drawfile constants, structures, SWI declarations, and helper prototypes.

Key behavior:
- Provides Draw/screen unit conversion macros.
- Defines DrawFile SWI numbers and object type/path type enums.
- Declares core Drawfile structures: font tables, text, paths, sprites, groups, tagged objects, text areas, options, transformed text/sprites, JPEGs, objects, and diagrams.
- Defines Drawfile error constants and path/text/render flag bits.
- Declares SWI wrappers and local helper functions for create, append, render, verify, and query operations.

Important details:
- Depends on DeskLib Sprite and Wimp types.
- Uses flexible one-element arrays for variable-sized Drawfile payloads.
- This is platform-specific support code preserved in the Antiword source tree.

Filesystem relevance:
- Indirect: describes serialized output layout for converted Draw files.
