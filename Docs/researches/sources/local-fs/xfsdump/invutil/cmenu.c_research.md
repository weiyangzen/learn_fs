# File Research: sources/local-fs/xfsdump/invutil/cmenu.c

Implements the curses menu controller for `xfsinvutil`.

Key functions:
- Defines key bindings for expand/collapse, delete/undelete, import, commit, quit, and select.
- `signal_handler()` rebuilds windows after `SIGWINCH`.
- `menu_commit()` walks menu nodes, calls node-specific commit handlers once, then frees the list.
- `menu_import()` prompts for an inventory path, loads its fstab subtree, and marks imported nodes.
- Expand/collapse helpers show/hide child nodes recursively.
- Delete/undelete helpers mark nodes and their descendants/ancestors.
- `list_prune()` applies node-specific prune predicates and delete/undelete operations.
- `generate_menu()` starts tree generation from fstab.
- `create_windows()` initializes curses pads/windows.
- `invutil_interactive()` runs the interactive menu and closes all mapped/open files at exit.

Important dependencies:
- Uses menu operations supplied by fstab, invidx, and stobj modules.
- Depends on `list.c`, `menu.c`, and `screen.c` for list allocation and UI drawing.

Notable observations:
- `list_delete()` has a likely bug: `if(current == NULL && current->data == NULL)` should use `||`; as written it can dereference null.
- Import marks text column `[1] = 'I'`, relying on generated display string layout.
