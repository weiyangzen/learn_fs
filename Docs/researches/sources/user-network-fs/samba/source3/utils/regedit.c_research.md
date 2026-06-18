<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit.c -->
# sources/user-network-fs/samba/source3/utils/regedit.c

## Purpose

`regedit.c` implements Samba's ncurses-based registry editor. It displays registry keys in a tree pane, values in a value pane, supports key/value creation, editing, deletion, search, refresh, resize handling, and opens the Samba3 registry backend.

## Important APIs, Types, and Functions

`struct regedit` holds the registry context, ncurses windows, tree view, value list, current input pane, and active search options. Major helpers are `show_path()`, `print_heading()`, `load_values()`, `add_reg_key()`, `regedit_search()`, `handle_tree_input()`, `handle_value_input()`, `handle_main_input()`, `regedit_getch()`, `display_window()`, and `main()`.

## Control Flow

`main()` initializes Samba cmdline state, disables logging noise, burns credentials from argv, opens the Samba3 registry through `reg_open_samba3()`, and calls `display_window()`. The UI initializes curses, colors, the root tree, key/value panes, and a global `regedit_main` used by `regedit_getch()`. The main loop reads keys until `q`, dispatches global commands first, then routes input to either the tree or value pane. Tree input navigates, loads children, ascends, creates keys/subkeys, and deletes keys after confirmation. Value input navigates, edits or creates values through dialog helpers, and deletes values after confirmation.

## State and Persistence Behavior

Registry mutations are persistent through `reg_key_add_name()`, `reg_key_del()`, `reg_val_set()` in dialog code, and `reg_del_value()`. UI state includes selected tree node, selected value item, cached tree children, value-list contents, active search query/options, and current focus pane. Refresh reopens the tree path from the registry context.

## Dependencies and Integration Points

It depends on ncurses/menu/panel, `regedit_treeview`, `regedit_valuelist`, `regedit_dialog`, Samba registry APIs, Samba cmdline credentials, loadparm, and the Samba3 wrapper declared in `regedit.h`.

## Risks and Edge Cases

The UI uses global `regedit_main`, making nested or concurrent editor instances unsafe. Many paths rely on `SMB_ASSERT()` after allocation or tree assumptions. Delete and edit operations reopen keys to refresh caches, but error handling for delete value ignores the returned `WERROR`. Search temporarily loads value lists for other keys and must restore visible state carefully. Small terminals can expose layout assumptions despite resize handling.

## Test Signals

Manual or scripted curses tests should cover navigation, resize, refresh, create/delete key, create/edit/delete each supported value type, binary edit mode, recursive and non-recursive search, case-sensitive search, and failure injection from registry wrappers. Terminal smoke tests on very small dimensions are useful.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit.c -->
