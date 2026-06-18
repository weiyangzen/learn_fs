# File Research: sources/os/bsd/netbsd-src/lib/libform/internals.c

Core implementation for NetBSD `libform` field editing internals. It manages field line lists, cursor state, tab expansion metadata, wrapping, curses redraw, field/page traversal, validation dispatch, and driver request handling.

Important responsibilities:
- Maintains `_FORMI_FIELD_LINES` linked lists, including free-list reuse, row copying, row destruction, line splitting, line joining, and hard-return propagation.
- Implements reversible word wrapping in `_formi_wrap_field`, backing up affected rows before mutating so failed wraps can restore prior state.
- Handles cursor movement and editing requests in `_formi_manipulate_field`, including char/line/word movement, insert/delete, clear-to-EOL/EOF/field, overlay/insert mode, and vertical/horizontal scrolling.
- Draws fields with curses in `_formi_redraw_field` and `_formi_draw_page`, applying field visibility/public/private behavior, foreground/background attributes, padding, justification, and tab expansion.
- Computes form page metadata, sorted field traversal order, and directional neighbors through `_formi_find_pages`, `_formi_sort_fields`, and `_formi_stitch_fields`.
- Dispatches character and full-field validation through linked `FIELDTYPE` chains and synchronizes editable line state back to buffer 0 via `_formi_sync_buffer`.

Notable implementation details:
- Tabs are treated as 8-column stops and cached in per-row `_formi_tab_t` lists.
- Single-line dynamic fields horizontally scroll; multiline fields scroll vertically and wrap.
- Validation honors `O_NULLOK`, `O_PASSOK`, `O_STATIC`, `O_WRAP`, `O_BLANK`, and type callbacks.
- The code is stateful and pointer-heavy; cursor fields such as `row_xpos`, `cursor_xpos`, `start_char`, `cursor_ypos`, `cur_line`, and `start_line` must remain consistent after edits.
