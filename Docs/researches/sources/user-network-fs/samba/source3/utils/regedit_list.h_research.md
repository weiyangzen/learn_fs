# sources/user-network-fs/samba/source3/utils/regedit_list.h

`regedit_list.h` declares the generic multicolumn list interface used by the registry editor UI. `struct multilist_accessors` is the integration contract: required callbacks provide first row, next row, and cell labels; optional callbacks provide headers, row count, previous row, row-by-index, and item prefixes. `struct multilist_column` exposes width and right-alignment metadata.

The public API covers creation, column configuration, window/data binding, refresh, cursor driving, and current-row get/set. Cursor commands are abstract enum values (`ML_CURSOR_UP`, `DOWN`, `PGUP`, `PGDN`, `HOME`, `END`) so consumers can map keys outside this layer.

The opaque `struct multilist` keeps implementation state private, but the contract implies that row pointers returned from callbacks are stable selection handles. Dependencies are Samba `includes.h`, `TALLOC_CTX`, `WERROR`, and ncurses `WINDOW`. Integration points are `regedit_treeview.c` and `regedit_valuelist.c`.

Risks are mostly contract-related: callers must provide non-null required callbacks, match the configured column count, and return strings/rows that remain valid during rendering. Test signals include a minimal accessor implementation, a fast accessor implementation with row counts and indexes, and compile-time checks for callback signature drift.
