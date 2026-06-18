# sources/user-network-fs/samba/source3/utils/regedit_treeview.h

`regedit_treeview.h` declares regedit's registry tree model and ncurses view wrapper. `struct tree_node` contains a display name, opened `registry_key`, parent, first child, and sibling links. `struct tree_view` contains root, frame/sub windows, panel, and the shared `multilist`.

The header exposes constructors, sibling operations, traversal, lazy child loading, path printing/getting, view construction/resizing/showing, root/path/current-node updates, selected-heading highlighting, and key reopening. Macros classify the artificial root and top-level hive nodes.

State and ownership are talloc-oriented, with keys expected to be owned by their nodes. The structs are public rather than opaque, so callers can inspect or mutate links directly. Dependencies are Samba basics, ncurses, panel, generic registry forward declarations, and the multilist forward declaration.

Risks come from that public layout: callers can break parent/child/sibling invariants, and macros assume well-formed non-null relationships. Test signals include structural invariant checks for root/hive/child nodes, traversal behavior, visibility checks, and build checks against `regedit_treeview.c`.
