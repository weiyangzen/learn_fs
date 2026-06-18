# sources/test-tools/kdevops/scripts/kconfig/lxdialog/util.c

## Purpose
`util.c` provides common ncurses setup, color themes, drawing primitives, text wrapping, ESC/resize handling, and item-list management shared by all lxdialog widgets.

## Important APIs, Types, And Functions
It defines global `saved_x`, `saved_y`, `dlg`, `item_cur`, `item_nil`, and `item_head`. Theme helpers include `set_mono_theme()`, `set_classic_theme()`, `set_blackbg_theme()`, `set_bluetitle_theme()`, `set_theme()`, `init_one_color()`, `init_dialog_colors()`, and `color_setup()`. Public utilities include `attr_clear()`, `dialog_clear()`, `init_dialog()`, `set_dialog_backtitle()`, `set_dialog_subtitles()`, `end_dialog()`, `print_title()`, `print_autowrap()`, `print_button()`, `draw_box()`, `draw_shadow()`, `first_alpha()`, `on_key_esc()`, `on_key_resize()`, and all `item_*` functions.

## Control Flow
`init_dialog()` initializes curses, validates terminal size, stores cursor position, selects a color theme from `MENUCONFIG_COLOR`, enables keypad/cbreak/noecho, and clears the background. Drawing helpers are called by widgets to render consistent boxes, titles, prompts, buttons, and shadows. `on_key_esc()` temporarily disables keypad and drains pending input to distinguish a real ESC from escape sequences. Item functions manage a singly linked list, append formatted text, set tags/data/selection, iterate, and retrieve current item fields.

## State And Persistence
All state is process-local ncurses and heap state. `item_reset()` frees the item list. There is no file persistence.

## Dependencies And Integration Points
It depends on ncurses and `dialog.h`, and every lxdialog widget depends on it. Menuconfig signal handling uses `saved_x`/`saved_y`.

## Risks And Test Signals
Several string operations assume prompt/item lengths fit fixed buffers (`strcpy` in `print_autowrap`, `vsnprintf` truncation for items). `item_make()` does not check allocation failure. `init_one_color()` monotonically consumes color pairs. Test signals include theme selection, no-color terminals, too-small terminal initialization, ESC behavior, text wrapping with long prompts, item reset/rebuild, and memory checking.
