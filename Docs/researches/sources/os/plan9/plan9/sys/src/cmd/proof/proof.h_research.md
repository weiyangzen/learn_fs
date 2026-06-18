# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/proof.h

Purpose: Shared definitions and declarations for the `proof` previewer.

Key contents:
- Limits for pages, fonts, sizes, minimum size, default magnification, maximum views.
- Externs for device name, magnification, view count, current position/font/size, scaling, offsets, cursor, font directory, debug, and resize flag.
- Declares screen, map, font, rendering, and buffered-input functions.
- Defines `dprint` debug macro.

Dependencies and integration:
- Included by `font.c`, `htroff.c`, `main.c`, and `screen.c`.

Risks and notes:
- Global-state API reflects small single-process viewer design.
