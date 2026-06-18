# sources/test-tools/kdevops/scripts/kconfig/lxdialog/menubox.c

## Purpose
`menubox.c` implements the main menu list widget for menuconfig. It shows selectable menu entries, supports scrolling, hotkeys, page navigation, and command buttons for select, exit, help, save, and load.

## Important APIs, Types, And Functions
The exported function is `dialog_menu(title, prompt, selected, s_scroll)`. Helpers include `do_print_item()`, `print_item` macro, `print_arrows()`, `print_buttons()`, and `do_scroll()`. It uses global item-list data and the `void *data` field to match the selected menu item.

## Control Flow
On resize it sizes the dialog to the current terminal, draws the prompt/list/buttons, restores a valid scroll offset from `*s_scroll`, and places the selected item in view. The key loop normalizes alphabetic hotkeys, searches visible entries, handles arrows, plus/minus, PageUp/PageDown, and updates scroll/highlight. Command keys return distinct codes for help, yes/no/module/toggle/search, button selection, and exit while saving the scroll position.

## State And Persistence
It mutates `*s_scroll` so callers can preserve scroll location across invocations and marks the selected item in the global item list. No disk state is used.

## Dependencies And Integration Points
It links into `mconf` and depends on shared lxdialog utilities. Return codes are part of the menuconfig frontend contract and must match caller expectations.

## Risks And Test Signals
The widget assumes item count and scroll math remain consistent while displayed. Return code meanings are implicit and easy to break. Tests should drive hotkeys, scrolling near boundaries, page navigation, saved scroll validation, each command key, resize, and empty list behavior.
