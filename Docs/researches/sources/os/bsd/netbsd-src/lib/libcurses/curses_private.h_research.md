# File Research: sources/os/bsd/netbsd-src/lib/libcurses/curses_private.h

Read completely: 434 lines.

This is the internal libcurses structure and helper declaration header. It defines `nschar_t`, `__LDATA`, `__LINE`, `WINDOW`, screen/window flags, color and pair structures, soft-label structures, ripoff-line structures, `SCREEN`, debug trace masks, common erase logic, internal function prototypes, and private extern globals.

Key internal state: `__LDATA` stores a character, attributes, continuation/background flags, and in wide builds a nonspacing list plus display width. `WINDOW` stores geometry, cursor position, line pointers, ownership pointers, flags, current/background attributes, background nonspacing list, pad refresh coordinates, and formatted I/O buffers. `SCREEN` stores terminal files, standard/current/virtual windows, terminal dimensions, ACS/WACS tables, color tables, termios modes, input keymap, unget buffer, resize state, soft-label state, and wide input conversion buffers.

Important interactions: this header is the integration contract for all source files in the group. It defines `__NEED_ERASE`, `__touchline`, `__sync`, `__mvcur`, key input initializers, color restore functions, nonspacing helpers, and window allocation internals.

Reliability notes: `__LDATA` layout is explicitly padding-sensitive. Many modules directly mutate line dirty markers and linked nonspacing lists, so changes here have broad ABI and memory-ownership impact.
