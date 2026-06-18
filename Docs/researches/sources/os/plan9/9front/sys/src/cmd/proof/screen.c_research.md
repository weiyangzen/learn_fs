# File Research: sources/os/plan9/9front/sys/src/cmd/proof/screen.c

Window, mouse, keyboard, menu, pan, resize, and confirmation handling for `proof`. It initializes draw/event, clears the screen, reads command strings from keyboard or mouse menus, supports tracking input-file changes, and defines cursors.

Key behavior:
- `getcmdstr` waits for mouse, keyboard, resize, or tracking timer events.
- Button 3 menu supports next, previous, page n, repaint, zoom, pan, and quit.
- `pan` moves screen contents interactively and updates `xyoffset`.
- `confirm` uses a special cursor and matching mouse button for dangerous menu entries.

Integration points:
- Uses Plan 9 `draw`, `event`, `cursor`, and `Dir` APIs.
- Returns command strings consumed by `htroff.c::botpage`.

Risks:
- Keyboard command buffer is fixed at 100 chars.
- `screenprint` draws black text on screen without clearing its previous text area, so prompts can overpaint.
