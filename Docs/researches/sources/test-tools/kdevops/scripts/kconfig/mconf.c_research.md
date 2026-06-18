# sources/test-tools/kdevops/scripts/kconfig/mconf.c

## Purpose
`mconf.c` implements the classic `menuconfig` terminal user interface for the vendored Linux Kconfig engine. It parses a Kconfig tree, loads the active `.config`, renders menus through `lxdialog`, lets users toggle symbols or enter string/int/hex values, supports symbol search, and writes `.config` plus generated autoconf output when the user exits.

## Important APIs, Types, And Functions
The UI is built around Kconfig `struct menu`, `struct symbol`, `struct property`, and `struct gstr` objects from `lkc.h`, plus the local search helpers in `mnconf-common.h`. Key functions are `main()`, `conf()`, `build_conf()`, `conf_choice()`, `conf_string()`, `conf_load()`, `conf_save()`, `search_conf()`, `show_help()`, `handle_exit()`, and `conf_message_callback()`. Global UI state includes `filename`, `indent`, `current_menu`, `child_count`, `single_menu_mode`, `show_all_options`, `save_and_exit`, `silent`, and a subtitle trail list.

## Control Flow
`main()` optionally enables silent mode, calls `conf_parse()` and `conf_read()`, checks `MENUCONFIG_MODE=single_menu`, initializes the dialog library, sets the config filename/backtitle, installs a Kconfig message callback, and repeatedly calls `conf(&rootmenu, NULL)` until exit is accepted. `conf()` rebuilds menu items with `build_conf()`, calls `dialog_menu()`, dispatches button/action return codes, and recurses into submenus or specialized editors. `build_conf()` filters invisible nodes unless show-all is enabled, formats menu items according to symbol type and dependency state, and recursively emits child entries. Search uses `sym_re_search()`, `get_relations_str()`, `handle_search_keys()`, and jump-key callbacks to move from results into the menu tree.

## State And Persistence
Interactive state is process-local: subtitle list, current menu path, scroll position, single-menu expansion stored in `menu->data`, and `show_all_options`. Persistent state is configuration data read through `conf_read()`, modified through `sym_set_*()`/`choice_set_value()`, saved via `conf_write()`, and finalized through `conf_write_autoconf(0)`. Alternate load/save dialogs can switch `filename` to a different config path.

## Dependencies And Integration Points
This file depends on the Kconfig core (`conf_parse`, `conf_read`, symbol/menu APIs), `lxdialog` widgets, ncurses through the dialog layer, `list.h`, `xalloc.h`, and shared search jump helpers from `mnconf-common.c`. It is normally built by Kconfig make rules as the `mconf` frontend and consumed through `make menuconfig`-style targets.

## Risks And Edge Cases
Terminal size and dialog initialization failures prevent use. User input validation depends on `sym_set_string_value()` and `sym_set_tristate_value()`, so dependency logic errors surface here as unchangeable or rejected options. Search allocates relation strings and jump entries per loop and must free them on every path. The local source contains duplicated text in `search_help` and a duplicated `if (sym->rev_dep.tri == mod)` line in the tristate renderer; these are likely copy artifacts and should be checked against upstream before changing behavior.

## Test Signals
Useful checks include building `mconf`, running it on a small Kconfig with bool/tristate/string/choice/menu entries, toggling `MENUCONFIG_MODE=single_menu`, exercising search and jump keys, saving/loading alternate configs, verifying `-s` silent behavior, and confirming invalid int/hex/string input is rejected without corrupting `.config`.
