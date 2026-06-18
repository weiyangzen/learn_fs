# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/text.c

Abaco text widget implementation: rune storage, frame rendering, editing, selection, scrolling, and mouse commands.

Key responsibilities:
- Initializes, redraws, resizes, closes, inserts into, deletes from, and fills `Text` frames.
- Handles typed input, navigation keys, URL-enter action, textarea editing, and erase-word/line.
- Implements frame auto-scroll during selection.
- Implements single/double-click selection, chorded cut/paste, and scroll-area behavior.
- Draws and maintains selection ranges in frame coordinates.
- Implements bracket/quote/newline matching for double-click.
- Routes button 1/2/3 to select, execute, and look behavior.

Important behavior:
- Non-textarea newline in URL tag triggers `Get`.
- Tag text ignores one-line scroll wheel keys.
- `textshow()` scrolls textarea origin to keep selection visible.
- Chording can undo immediate cut/paste state while the mouse button is held.
- `textsetorigin()` reuses frame contents when scrolling by small deltas.

Dependencies:
- Uses Plan 9 frame library, Abaco command functions, scroll helpers, snarf helpers, and global selection state.

Notable risks:
- Text operations assume `Text.rs.r` has enough trailing room for NUL after deletion; insert allocation is exactly `nr+n`, so NUL writes after delete rely on prior capacity.
- Complex selection paths are stateful across globals `clicktext`, `selecttext`, `argtext`, and mouse controller state.
