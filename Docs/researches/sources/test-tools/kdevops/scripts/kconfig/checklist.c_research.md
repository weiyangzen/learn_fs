# sources/test-tools/kdevops/scripts/kconfig/checklist.c

## Purpose
This file implements an ncurses checklist/radiolist dialog for the Kconfig menu frontend. It displays items maintained by the shared lxdialog item list and lets the user select exactly one item or request help.

## Important APIs, Types, And Functions
The exported API is `dialog_checklist(title, prompt, height, width, list_height)`. Internal helpers are `print_item()`, `print_arrows()`, and `print_buttons()`. It relies on global dialog theme state `dlg`, item-list functions such as `item_foreach()`, `item_set()`, `item_str()`, `item_is_tag()`, `item_set_selected()`, and ncurses `WINDOW` objects.

## Control Flow
The dialog selects an initial highlighted row from an item tagged `X` or an item already selected. On each resize it validates minimum terminal dimensions, centers a dialog, draws a bordered list subwindow, computes checkbox and item columns, scrolls to keep the selected choice visible, renders visible items, then enters a key loop. Arrow keys, `+`, `-`, and first-letter hotkeys move the highlight. Space, Enter, or `s` selects the current item; `h`/`?` returns the Help button; Tab and horizontal arrows switch buttons; ESC and resize are handled through common helpers.

## State And Persistence
State is in local `choice`, `scroll`, and `button` variables, plus static layout globals `list_width`, `check_x`, and `item_x`. The persistent side effect is updating the selected flag in the global item list. No files are touched.

## Dependencies And Integration Points
It integrates with `mconf` through `dialog.h` and `util.c` item-list and drawing utilities. Return values are button indices or key/error codes consumed by menuconfig logic.

## Risks And Test Signals
The file is similar to `lxdialog/checklist.c`, so duplicate maintenance is a risk. `malloc()` return values are unchecked. Long item strings are truncated; empty strings can still index `list_item[0]`. Curses tests should exercise resize, scrolling boundaries, hotkeys, tagged separators, selected item persistence, and too-small terminal returns.
