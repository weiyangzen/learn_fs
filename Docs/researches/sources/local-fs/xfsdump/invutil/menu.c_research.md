# File Research: sources/local-fs/xfsdump/invutil/menu.c

Implements the ncurses menu event loop for interactive `xfsinvutil`.

Core behavior:
- `put_all_options()` renders all non-hidden nodes and highlights the current node.
- `put_helpscreen()` creates a temporary reversed-color help window listing key bindings.
- `menu()` drives keyboard navigation and operation dispatch.

Navigation:
- Up/down: previous/next visible node, also bound to `k`/`j`.
- Right/left: child/parent traversal, also bound to `l`/`h`.
- `?` or F1: help.
- Other keys are matched against `menukey_t` bindings.

Integration:
- Uses global `mainmenu`, `infowin`, `redraw_screen`, and `redraw_options`.
- Calls per-node operation hooks for highlight/unhighlight and keyed actions.
- Handles `ERR` with `errno == EINTR` by switching to recreated `mainmenu`, supporting terminal resize handling elsewhere.

Notable issue:
- `if(current == NULL && current->data == NULL)` should likely be `||`; as written it dereferences `current` if `current == NULL`.
