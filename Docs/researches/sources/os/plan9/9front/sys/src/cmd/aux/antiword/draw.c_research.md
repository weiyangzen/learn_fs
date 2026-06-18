# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/draw.c

RISC OS Draw-format output backend and GUI display integration for Antiword.

Important behavior:
- Provides fallback `flex_alloc`, `flex_free`, and `flex_extend` when not using GCC.
- Creates main and scale windows from RISC OS templates.
- `pCreateDiagram()` allocates a `diagram_type`, initializes Drawfile memory, windows, scale factor, bounding box, and source filename.
- `vExtendDiagramSize()` grows Drawfile backing memory in 4 KiB increments.
- `vPrologue2()` emits a Draw font table from Antiword’s font table.
- `vSubstring2Diagram()` appends text objects with bounding boxes, font style, color, baseline, superscript/subscript offsets, and advances current X position.
- `vImage2Diagram()` embeds sprite or JPEG image objects and updates position.
- `bAddDummyImage()` adds a placeholder rectangle for missing images.
- Paragraph/page/list/table functions mostly adjust positions or are dummy no-ops for Draw output.
- GUI handlers manage window redraw, title updates, save/scale menu actions, keyboard shortcuts, caret placement, and scaling.

Filesystem/output relevance:
- Builds an in-memory Drawfile object stream from parsed Word content, then supports display/save workflows on RISC OS.
