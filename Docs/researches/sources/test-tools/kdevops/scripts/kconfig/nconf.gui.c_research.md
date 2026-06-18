# sources/test-tools/kdevops/scripts/kconfig/nconf.gui.c

## Purpose
`nconf.gui.c` contains reusable ncurses UI primitives for `nconf`: color attribute setup, centered headings, text wrapping helpers, button dialogs, input dialogs, scrollable text windows, and window refresh orchestration.

## Important APIs, Types, And Functions
Exports include global `attr_*` variables declared in `nconf.h`, `set_colors()`, `print_in_middle()`, `get_line_no()`, `get_line()`, `get_line_length()`, `fill_window()`, `btn_dialog()`, `dialog_inputbox()`, `refresh_all_windows()`, `show_scroll_win()`, and `show_scroll_win_ext()`. It uses `struct nconf_attr_param` to initialize color/no-color themes.

## Control Flow
`set_colors()` detects color support, initializes default-color pairs, and writes each attribute global. Text helpers count and slice newline-delimited strings. `btn_dialog()` creates a centered window with optional button menu, handles left/right/enter/escape/function-key input, and returns the selected index or `KEY_EXIT`. `dialog_inputbox()` creates a prompt and editable single-line input area with cursor movement, insertion, deletion, dynamic buffer expansion, and help/exit signaling. `show_scroll_win_ext()` creates a pad for text, copies viewport slices into a bordered window, supports vertical/horizontal scrolling, and delegates extra keys to an optional callback.

## State And Persistence
State is curses window/panel/menu/item objects and caller-owned input buffers. The only exported persistent process state is the color attribute globals. No disk persistence occurs.

## Dependencies And Integration Points
Depends on `nconf.h`, `lkc.h`, `xalloc.h`, and ncurses menu/panel APIs. `nconf.c` uses these routines for all dialogs, help panes, and search result panes. `show_scroll_win_ext()` integrates with `mnconf-common` through an extra-key callback signature.

## Risks And Edge Cases
The local source shows a duplicated `int win_lines = 0;` declaration in `show_scroll_win_ext()`, likely a compile error. In `fill_window()`, `tmp[len] = '\0'` can write past the copied width if `len > x` because the copy length is clamped but the terminator index is not. `dialog_inputbox()` uses plain `realloc()` without the xalloc exit-on-failure behavior in one path. Very small terminal sizes can produce zero/negative derived dimensions.

## Test Signals
Compile with warnings, run under color and monochrome terminals, test long lines, long input, backspace/delete/home/end, scrollable content larger than the screen, search-result numeric callbacks, ESC/F5/F9 exits, and terminal resize paths through `nconf.c`.
