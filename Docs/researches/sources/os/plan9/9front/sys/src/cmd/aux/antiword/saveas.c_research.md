# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/saveas.c

RISC OS GUI “Save as” handlers for text and Draw output.

Key responsibilities:
- Creates and initializes the `xfer_send` save window.
- Saves Draw diagram text objects as a plain text file.
- Saves Draw diagram objects as a Draw file after translating Y coordinates from top-left to bottom-left origin.
- Handles menu and keyboard events for text or Draw saves.
- Sets output filetypes after successful saves and removes partial files on failure.

Important behavior:
- Text export reconstructs line breaks from text object bounding boxes and indentation from X positions.
- Draw export adjusts bounding boxes, text baselines, path coordinates, sprites, and JPEG transforms.
- Unknown Draw object types abort the save.

Dependencies:
- DeskLib menu/save/template/window APIs, Drawfile structures, RISC OS filetype helpers.

Research relevance:
- GUI/export adapter for RISC OS Antiword; not part of Word parsing itself.
