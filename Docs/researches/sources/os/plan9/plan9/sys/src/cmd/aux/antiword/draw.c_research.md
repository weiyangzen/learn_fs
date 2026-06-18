# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/draw.c

This RISC OS-specific file builds, displays, scales, and manages Antiword Draw-format diagrams.

Key behavior:
- Provides fallback `flex_alloc/free/extend` wrappers for non-GNUC builds.
- Creates main and scale-view windows from templates.
- Allocates and initializes a Draw diagram with default memory and bounding box.
- Appends font tables, text objects, sprite/JPEG images, and dummy image placeholders.
- Tracks current output coordinates and paragraph/page movement.
- Implements RISC OS window redraw, title, keyboard, mouse, save-menu, and scale controls.
- Verifies and destroys diagrams, including cleanup of event-message references.

Important details:
- Diagram memory grows in 4 KiB increments from an initial 32 KiB.
- Text positioning accounts for font size, baseline, superscript, and subscript.
- Several list/table/header methods are dummy no-ops for Draw output.
- Uses DeskLib, Wimp, Drawfile, and flexlib APIs; not Plan 9 runtime code.

Filesystem relevance:
- Indirect: output rendering path for converted Word content, including save actions, but not filesystem internals.
