# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/ico.c

This is an ICO file reader/viewer and optional image extractor.

Key behavior:
- Parses ICO headers and directory entries.
- Supports icon payloads that are embedded PNGs or BMP-style DIB data.
- Converts paletted BMP icons through a Plan 9 colormap, handles XOR image data and optional AND masks.
- Displays all icons in a grid-like window and shows dimensions on hover.
- Right-click menu can write selected image or mask; `-c` writes the first icon image to stdout.

Research notes:
- Uses `memdraw` `Memimage` internally and converts to display `Image` row by row.
- For BMP icons, it composites image plus mask over white before display/export.
