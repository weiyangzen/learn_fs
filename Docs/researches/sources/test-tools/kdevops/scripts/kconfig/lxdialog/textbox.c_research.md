# sources/test-tools/kdevops/scripts/kconfig/lxdialog/textbox.c

## Purpose
`textbox.c` implements a scrollable read-only text dialog for help and informational content in menuconfig.

## Important APIs, Types, And Functions
The public function is `dialog_textbox(title, tbuf, initial_height, initial_width, _vscroll, _hscroll, extra_key_cb, data)`. Internal state and helpers include static `hscroll`, `begin_reached`, `end_reached`, `page_length`, `buf`, `page`, `start`, `end`, `back_lines()`, `get_line()`, `print_line()`, `print_page()`, `print_position()`, and `refresh_text_box()`.

## Control Flow
The dialog initializes `page` into the text buffer, applies optional saved vertical/horizontal scroll, sizes/draws the window, prints the first page, and loops on keys. Home/End jump to top/bottom; up/down and page keys move vertically; left/right and `0` control horizontal scroll; exit keys close; resize recreates the window after backing up; unknown keys may be delegated to `extra_key_cb`, which can request exit.

## State And Persistence
Scroll state is stored back through `_vscroll` and `_hscroll` pointers. The text buffer is caller-owned and read-only. Static module variables mean simultaneous textboxes are not reentrant.

## Dependencies And Integration Points
It depends on lxdialog drawing functions, ncurses, and optional caller callbacks. Menuconfig uses it for help text and extended descriptions.

## Risks And Test Signals
`print_position()` divides by `strlen(buf)`, so an empty buffer risks division by zero. Lines longer than `MAX_LEN` are truncated. Scrolling works by pointer arithmetic over bytes, not characters. Tests should cover empty text, long lines, saved scroll restore, top/bottom boundaries, horizontal scrolling, callback exit, and resize.
