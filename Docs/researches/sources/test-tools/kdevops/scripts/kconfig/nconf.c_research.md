# sources/test-tools/kdevops/scripts/kconfig/nconf.c

## Purpose
`nconf.c` implements the ncurses menu/form/panel Kconfig frontend. It offers richer keyboard navigation than `mconf`, including function-key commands, incremental menu search, symbol search, single-menu mode, save/load dialogs, and choice/string editors.

## Important APIs, Types, And Functions
Key state includes `struct mitem`, `MAX_MENU_ITEMS`, `show_all_items`, `indent`, `current_menu`, `child_count`, `single_menu_mode`, `main_window`, `curses_menu`, `curses_menu_items`, `k_menu_items`, `items_num`, `global_exit`, `dialog_input_result`, and `dialog_input_result_len`. Key functions include `main()`, `setup_windows()`, `selected_conf()`, `conf()`, `build_conf()`, `show_menu()`, `do_match()`, `get_mext_match()`, `conf_choice()`, `conf_string()`, `conf_load()`, `conf_save()`, `search_conf()`, `do_exit()`, and the F1-F9 handlers.

## Control Flow
`main()` parses Kconfig and config state, reads `NCONFIG_MODE`, initializes curses, verifies terminal size, configures the curses menu, creates windows, installs message callbacks, and loops through `conf(&rootmenu)` until `global_exit`. `selected_conf()` rebuilds menu items, restores active item selection, renders via `show_menu()`, handles incremental search and special keys, then toggles symbols or enters submenus/editors. `build_conf()` mirrors `mconf` rendering but creates ncurses `ITEM`s. `conf_choice()` renders a choice list and applies `choice_set_value()`. F-key handlers invoke help, symbol info, show-all toggle, save, load, search, and exit.

## State And Persistence
Process state is mostly global UI state plus allocated curses items/windows. Menu expansion in single-menu mode is stored in `menu->data`. Persistent config changes are made through Kconfig symbol setters and saved with `conf_write()`/`conf_write_autoconf()`. Dialog input storage is dynamically resized and reused.

## Dependencies And Integration Points
Depends on Kconfig core APIs, `mnconf-common.c` for search jumps, `nconf.gui.c`/`nconf.h` for dialogs/colors, and ncurses `menu`, `panel`, and `form` libraries. It integrates with build detection through `nconf-cfg.sh`.

## Risks And Edge Cases
The local source contains apparent copy damage: a duplicated brace in `function_keys`, duplicated `switch (res)`, and a double opening brace in `build_conf()`. These may prevent compilation. `MAX_MENU_ITEMS` silently caps item creation. Incremental search manipulates `pattern[strlen(pattern)-1]` on backspace without an explicit non-empty guard. UI behavior depends heavily on terminal capabilities and dimensions.

## Test Signals
Compile `nconf`; run with small and large Kconfig trees; exercise F1-F9, no-function-key fallback, incremental search/backspace, symbol search jump keys, save/load, choice editing, string/int/hex editing, terminal resize, `NCONFIG_MODE=single_menu`, and show-all toggling.
