# File Research: sources/os/bsd/netbsd-src/lib/libedit/read.c

## Purpose
Implements terminal input reading and the main edit loop for wide-character libedit input.

## Main Interfaces
- `read_init`, `read_end`: allocate/free `el_read_t` and macro stack.
- `el_read_setfn`, `el_read_getfn`: install/query custom character reader.
- `el_wpush`: push a macro string onto the input stack.
- `el_wgetc`: read one wide character from macros or terminal.
- `read_prepare`, `read_finish`: set signal/raw/cooked terminal state around editing.
- `el_wgets`: main line-input loop.
- `noedit_wgets`: plain read path for no-tty or disabled editing.

## Control Flow
`el_wgets` prepares terminal state, then repeatedly:
1. Reads the next command/character through `read_getcmd`.
2. Resolves key macros and the active key map.
3. Invokes the mapped editor function from `el->el_map.func`.
4. Handles command return codes such as refresh, cursor-only movement, newline, EOF, fatal reset, or error beep.
5. Restores terminal state and returns the edited line.

`read_char` reads bytes from `el_infd`, decodes them with `mbrtowc`, handles invalid/incomplete multibyte sequences, and reacts to signal flags set by `sig.c`.

## Dependencies
Uses `map.c`, `keymacro.c`, `refresh.c`, `terminal.c`, `tty.c`, `sig.c`, character editing state, and generated editor command IDs from `fcns.h`.

## Risks And Notes
- The macro stack is capped at `EL_MAXMACRO` and failed pushes beep.
- `read__fixio` may modify descriptor blocking flags to recover from nonblocking reads.
- Signal handling is intertwined with read retry logic; `SIGWINCH` and `SIGCONT` trigger resize/refresh paths.
