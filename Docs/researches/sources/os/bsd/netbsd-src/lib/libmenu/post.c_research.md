# File Research: sources/os/bsd/netbsd-src/lib/libmenu/post.c

Implements `post_menu()` and `unpost_menu()`. Posting validates state, runs menu/item init hooks under `in_init`, checks window dimensions, clears item selections for non-radio menus, marks the menu posted, and draws it. Unposting runs termination hooks, clears `posted`, erases the screen window, and refreshes.

Important dependencies: `<menu.h>`, `<stdlib.h>`, and `internals.h`.

Notable behavior: `post_menu()` checks horizontal room but not an equivalent vertical-room condition. Hook calls are protected from reentrant state-changing APIs through `menu->in_init`.
