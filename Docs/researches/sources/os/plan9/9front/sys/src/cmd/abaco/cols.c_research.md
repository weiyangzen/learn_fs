# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/cols.c

Column-level layout and window management for the Abaco browser UI.

Key responsibilities:
- Initializes column tags and column background/borders.
- Adds, removes, closes, resizes, sorts, grows, and drags windows in a column.
- Maintains `Column.w[]`, `Column.nw`, and `Column.safe` layout state.
- Routes mouse/keyboard hits inside a column to column tags or contained windows.
- Checks column cleanliness through contained windows.

Important behavior:
- New windows split an existing window or steal half of the last window by default.
- `colgrow()` supports fixed repair, full-column expansion, maximum expansion, and incremental growth.
- Dragging can move a window to another column, reorder it, or resize the boundary with the previous window.
- `Column.safe == FALSE` represents an obscured/full-size layout state that must be repaired before some operations.

Dependencies:
- Uses `Text`, `Window`, `Row`, screen drawing, mouse state helpers, and window resize/tag APIs.

Notable risks:
- Manual rectangle arithmetic must maintain non-overlap and minimum usable heights.
- `realloc(c->w, c->nw*sizeof(Window*))` with zero count depends on Plan 9 libc behavior.
