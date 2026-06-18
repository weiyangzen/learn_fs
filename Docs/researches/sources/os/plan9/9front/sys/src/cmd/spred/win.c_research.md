# File Research: sources/os/plan9/9front/sys/src/cmd/spred/win.c

`win.c` implements window lifecycle and focus management for `spred`, using Plan 9 draw/mouse/frame primitives and the local `Wintab` type dispatch table.

Key responsibilities:
- Allocates the backing `Screen`, per-window color images, inverse-color image, and initial command window in `initwin`.
- Creates windows with `newwin`, links them into the global `wlist`, optionally links them into a file’s window list, initializes type-specific state via `w->tab->init`, and draws through `w->tab->draw`.
- Supports mouse-created windows (`newwinsel`), zero-copy/clone-like window duplication (`winzerox`), close (`winclose`), focus/top-window ordering (`setfocus`), point hit-testing (`winpoint`), click dispatch (`winclick`), and button-selected target windows (`winsel`).
- Handles explicit window resize and global screen resize, scaling all window rectangles proportionally after `getwindow`.

Important state:
- Global `scr`, `wlist`, `flist`, `actw`, `actf`, `cmdw`, `invcol`.
- `tabs[]` maps `CMD`, `PAL`, and `SPR` to external `cmdtab`, `paltab`, and `sprtab`.

Integration notes:
- File windows hold references to `File`; `winclose` refuses to close dirty last references once, setting `change = -1`.
- Most behavior is delegated through `Wintab` callbacks, so this file owns geometry/focus and leaves window content semantics elsewhere.

Risks:
- Uses intrusive linked lists and manual image lifetime management; incorrect `File` reference/list invariants could leak or use freed windows.
- `resize` rescales by old screen dimensions and assumes nonzero dimensions.
