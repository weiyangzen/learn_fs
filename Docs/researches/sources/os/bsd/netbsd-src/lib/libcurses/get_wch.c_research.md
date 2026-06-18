# File Research: sources/os/bsd/netbsd-src/lib/libcurses/get_wch.c

Read completely: 612 lines.

This file implements wide-character input: `__init_get_wch`, internal wide `inkey`, `get_wch`, `mvget_wch`, `mvwget_wch`, `wget_wch`, `unget_wch`, and `__fgetwc_resize`.

`__init_get_wch` initializes the screen's circular byte buffer and wide input state. The internal `inkey` is a state machine over `INKEY_NORM`, `INKEY_ASSEMBLING`, `INKEY_BACKOUT`, `INKEY_TIMEOUT`, and `INKEY_WCASSEMBLING`. It combines keypad trie matching with multibyte decoding via `mbrtowc`, inter-character timeouts, disabled key handling, and fallback return of raw characters when sequences fail.

`wget_wch` refreshes touched windows before input, handles resize events, serves pushed-back characters from the shared unget buffer, temporarily switches to cbreak when echoing outside raw mode, applies window delay/keypad modes, echoes regular wide characters through `setcchar`/`wadd_wch`, handles erase-like key symbols during echo, maps carriage return to newline when `nl` is active, and returns either `OK`, `ERR`, or `KEY_CODE_YES`.

Important interactions: shares `_cursesi_state` with `getch.c`, uses the same keymap trie, uses `_cursesi_screen->sp` conversion state and `cbuf`, calls `__timeout`, `__notimeout`, `__delay`, `__save_termios`, `__restore_termios`, `resizeterm`, and `__unget`.

Reliability notes: `__fgetwc_resize` does not set `*resized` on the non-resize error path, but `wget_wch` checks that bool after `WEOF`; this can read an uninitialized local. The state machine exits with `exit(2)` if it sees an invalid internal state.
