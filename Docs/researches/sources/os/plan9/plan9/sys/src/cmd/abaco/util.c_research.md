# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/util.c

General utilities for Abaco: allocation, runes, dimensions, colors, fonts, process execution, charset conversion, image fixups, refresh messages, and mouse helpers.

Key responsibilities:
- Provides checked allocation/reallocation/string helpers.
- Converts bytes to runes and manages `Runestr` lifetime/copy/equality.
- Provides word/blank scanning and item classification helpers.
- Resolves dimension values and distributes flexible dimensions.
- Looks up page background/base URL metadata.
- Allocates colors/images, draws 3D rectangles/ellipses, initializes fonts, and caches colors/fonts.
- Parses plumb attributes into runes.
- Validates URLs using a compiled regex.
- Executes shell commands with redirected pipes via `/bin/rc -c`.
- Converts charsets via built-in Latin-1/Windows control mapping or external `tcs`.
- Detects charset from HTTP content type, XML declaration, or HTML meta tags.
- Maps x coordinates to text indices and tests whether a rectangle contains selected text.
- Loads images into draw images, rewrites/merges text items, queues refresh messages, and saves/restores/clears mouse state.
- Creates a new browser window in the current column.

Dependencies:
- Includes `fonts.h` and `tcs.h`.
- Uses Plan 9 draw, memdraw, thread, regexp, and process APIs plus external `tcs`.

Notable risks:
- Several helpers shell out or depend on installed Plan 9 commands.
- Charset detection is heuristic and comment notes servers may lie.
- Global caches for fonts/colors/refresh/mouse state need disciplined lifecycle handling.
