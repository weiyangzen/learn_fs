# sources/user-network-fs/samba/source3/utils/regedit_treeview.c

`regedit_treeview.c` implements regedit's registry key browser. It models keys as talloc-owned `tree_node` objects with parent/child/sibling links, lazily loads subkeys from the generic registry API, traverses siblings or depth-first, and renders the visible sibling level through `multilist`.

Important APIs include `tree_node_new`, `tree_node_new_root`, sibling list helpers, `tree_node_next`, `tree_node_prev`, `tree_node_load_children`, `tree_node_reopen_key`, `tree_node_get_path`, `tree_node_print_path`, and view functions such as `tree_view_new`, `tree_view_resize`, `tree_view_set_path`, `tree_view_update`, and `tree_view_driver`. Static multilist accessors expose a single `Name` column with `+` for nodes that have children.

Root creation adds available hives under an artificial `ROOT`. Loading a node queries subkey count, enumerates names, opens child keys, creates nodes, sorts them, and links the list. The view owns a boxed ncurses window, subwindow, panel, root, and multilist.

State is a cached tree of opened registry handles; children persist once loaded. Integration is between registry backends and higher-level regedit UI. Risks include registry calls during rendering via `tree_node_has_children`, path setting that can silently stop if a component is missing, and public linked-list invariants. Test signals: unavailable hives, sorted children, depth traversal, resize repainting, path reconstruction, and reopen after key mutation.
