# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/cols.c

Column management for Abaco’s Acme-like browser layout.

Key responsibilities:
- Initializes column tags and window arrays.
- Adds, clones, closes, and closes all windows in a column.
- Resizes windows when the column rectangle changes.
- Sorts windows by vertical position.
- Implements grow and drag behavior for resizing or moving windows.
- Dispatches pointer/key events to column tag or contained windows.
- Reports column cleanliness by checking all windows.

Dependencies:
- Uses `Window`, `Text`, `Row`, global mouse state, drawing primitives, and helpers from `dat.h`/`fns.h`.
- Coordinates with `wininit`, `winresize`, `winclose`, `winmouse`, `wintype`, and row layout.

Notable risks:
- Much of the behavior is interactive geometry code; correctness depends on rectangle invariants and mouse-button state.
- Window arrays are manually reallocated and compacted.
