# File Research: sources/os/plan9/9front/sys/src/cmd/acme/wind.c

Implements Acme window lifecycle, rendering, locking, tag generation, dirty tracking, event queuing, and window metadata operations.

Important behavior:
- `wininit` creates tag/body `Text` objects, optionally cloning body state and tag contents.
- `winresize` recomputes tag/body rectangles, redraws buttons, and protects mouse placement during tag expansion.
- `winlock` locks all windows sharing the same file; `winunlock` releases in reverse order to avoid file/text mutation hazards.
- `winsettag1` reconstructs command tags including `Del`, `Snarf`, `Undo`, `Redo`, `Put`, `Get`, and the user-editable bar suffix.
- `winaddincl` validates include directories and stores them on the window.
- `winevent` appends Acme event protocol messages and wakes blocked event readers.

The file is tightly coupled to Acme’s shared `File`, `Text`, `Column`, draw-state, and event model.
