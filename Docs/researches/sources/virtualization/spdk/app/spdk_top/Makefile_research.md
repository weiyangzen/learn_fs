# File Research: sources/virtualization/spdk/app/spdk_top/Makefile

This makefile builds the `spdk_top` terminal monitor from `spdk_top.c`. It includes SPDK common rules, sets `APP = spdk_top`, and links only the SPDK `rpc` library from `SPDK_LIB_LIST`.

The app also links ncurses UI libraries through `LIBS=-lpanel -lmenu $(shell pkg-config --libs ncurses)`, matching the source file's use of curses windows, panels, and menus. It uses the standard `mk/spdk.app.mk` application rule file and standard install/uninstall macros.

The narrow SPDK library dependency is significant: `spdk_top` does not embed target functionality. It connects to a running SPDK application's JSON-RPC socket and displays runtime state.
