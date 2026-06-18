# File Research: sources/os/bsd/netbsd-src/lib/libcurses/keymap.h

Defines private keymap structures shared by narrow and wide input handling.

It declares `key_entry_t`, keymap entry types (`KEYMAP_MULTI`, `KEYMAP_LEAF`), `MAX_CHAR`, allocation chunk size, circular input-buffer increment macro, input parser states including wide assembly, and `struct tcdata` mapping terminfo capability codes to curses key symbols.
