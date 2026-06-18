# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/saveas.c

This RISC OS file implements Save As handlers for generated Antiword diagrams.

Key behavior:
- Wraps DeskLib `Save_InitSaveWindowHandler` for text and Draw file output.
- `bText2File()` walks drawfile objects and writes text objects with inferred newlines and indentation.
- `bDraw2File()` writes a Draw file while translating Y coordinates from Antiword’s top-left layout to Draw’s bottom-left origin.
- Handles text, font-table, path, sprite, and JPEG drawfile object types.
- `bSaveTextfile()` and `bSaveDrawfile()` trigger saves from menu events or keyboard shortcuts.

Important details:
- Failed saves remove the partially written destination.
- Successful saves assign RISC OS filetypes for text or Draw files.

Filesystem relevance:
- Direct user-facing file creation and metadata setting for exported results.
