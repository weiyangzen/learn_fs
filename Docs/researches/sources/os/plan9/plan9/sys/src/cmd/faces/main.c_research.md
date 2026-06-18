# File Research: sources/os/plan9/plan9/sys/src/cmd/faces/main.c

Main GUI and process orchestration for the Plan 9 `faces` mail notifier.

Key behavior:
- Initializes draw state, colors, arrow masks, fonts, mouse, plumbing, and maildir configuration.
- Maintains an array of `Face*` entries, with visible window bounds `first` and `last`.
- Draws date/time, face icons, user labels, message times, unknown-domain overlays, and scroll arrows.
- Runs separate processes for minute clock updates and mouse handling; the main process receives faces through `nextface()`.
- Supports history mode, initial mailbox loading, scroll navigation, deletion handling, and click-to-show mail.

Important implementation details:
- Layout uses fixed 48x48 face cells and computed `nacross`/`ndown` based on window size.
- `facetime()` switches from `HH:MM` to `Mon DD` after 18 hours.
- `addface()` inserts new faces at index zero and shifts the displayed grid by screen copy operations.
- `delface()` removes and compacts entries while redrawing only affected cells.
- `killall()` posts notes to sibling processes before exit.

Risks and invariants:
- Display access is guarded by Plan 9 display locks after `display->locking = 1`.
- Geometry assumes the window can hold at least one face; very small windows may create tight layout edge cases.
