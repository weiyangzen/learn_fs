# File Research: sources/local-fs/xfsdump/invutil/cmenu.h

Declares curses menu types, globals, convenience macros, and operations.

Key contents:
- Defines info-window size and macros for header/footer/error/info/option drawing.
- Defines `alignment_t`.
- Defines `menu_ops_t`, the per-node operation vtable used by fstab, index, and storage-object nodes.
- Defines `menukey_t` for key binding dispatch.
- Defines shared fileinfo structs for mapped fstab, invidx, and stobj files.
- Declares global curses windows and redraw flags.
- Declares menu/list operation entry points and `generate_menu()`.

Important dependencies:
- Includes private inventory structures, so invutil edits the raw on-disk format directly.
- Depends on `list.h` `node_t`/`data_t` definitions.

Notable observations:
- This header is the coupling point between generic curses menu code and inventory-specific file editors.
