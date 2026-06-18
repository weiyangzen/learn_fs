# File Research: sources/os/plan9/plan9/sys/src/cmd/proof/screen.c

Purpose: Manages window initialization, keyboard/mouse commands, panning, menus, and cursors for `proof`.

Key behavior:
- `mapscreen` initializes draw and event handling.
- `clearscreen` clears display.
- `screenprint` writes prompt/status text.
- `getcmdstr` waits for resize, mouse, keyboard, or tracking timer events and returns command strings for `htroff.c`.
- Keyboard input accumulates a line until newline/return/view key.
- Mouse button 1 pans, button 3 opens menu, button 2 is effectively continue/no-op.
- Menu commands map to next, previous, page prompt, repaint, bigger, smaller, pan, and quit confirmation.
- Defines custom cursors: deadmouse, blot, skull.

Dependencies and integration:
- Uses Plan 9 `event` library and `proof.h`.
- Commands returned here are interpreted by `botpage`.

Risks and notes:
- `confirm` lacks an explicit return type in old C style.
- Tracking reload uses modification time polling.
- Panning scrolls the current screen image and updates global `xyoffset`.
