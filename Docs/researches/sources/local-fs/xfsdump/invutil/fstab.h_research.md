# File Research: sources/local-fs/xfsdump/invutil/fstab.h

Declares invutil fstab operations.

Key contents:
- `generate_fstab_menu()` for building the fstab subtree.
- File lifecycle helpers: `open_fstab()`, `close_all_fstab()`, `remmap_fstab()`.
- Matching helper: `find_matching_fstab()`.
- Menu operations: select, highlight, commit, prune.

Important dependencies:
- Includes `inv_priv.h`, `list.h`, and `cmenu.h`, so declarations expose curses/menu and private inventory types.
