# sources/user-network-fs/samba/source3/utils/regedit_list.c

`regedit_list.c` implements `struct multilist`, a reusable ncurses-backed table/pad widget used by Samba's terminal registry editor. It separates presentation from data with `struct multilist_accessors`, then handles column sizing, header drawing, row rendering, cursor movement, scrolling, and window resize rerendering.

Important APIs are `multilist_new`, `multilist_column_config`, `multilist_set_window`, `multilist_set_data`, `multilist_refresh`, `multilist_driver`, `multilist_get_current_row`, and `multilist_set_current_row`. Private helpers provide fallback row count, previous-row, and row-by-index behavior when accessors are absent. `put_item`, `put_header`, `put_data`, and `calc_column_widths` render and truncate columns.

Construction allocates talloc state, installs a destructor, and binds an ncurses window. `multilist_set_data` recalculates widths, recreates the pad, draws headers and all rows, and initializes selection. `multilist_driver` maps cursor commands to row changes and keeps the selected row visible through `fix_start_row`.

State is in-memory UI state only. The opaque source data is not owned by the list and row pointers must stay stable. Dependencies include talloc, `WERROR`, `SMB_ASSERT`, ncurses, and `regedit.h`; consumers include tree and value views. Risks include pointer-identity selection, O(n) fallback traversal for large lists, and edge behavior for empty data. Test signals: empty lists, truncation, right alignment, page/home/end navigation, resize selection preservation, and repeated reload leak checks.
