# File Research: sources/os/bsd/netbsd-src/lib/libedit/el.c

This file implements the core wide-character `EditLine` lifecycle and configuration API.

Key entry points:
- `el_init()` and `el_init_fd()` create an `EditLine`.
- `el_init_internal()` allocates and initializes the full editor object.
- `el_end()` tears down all modules and conversion buffers.
- `el_reset()` resets tty mode and character editor state.
- `el_wset()` and `el_wget()` implement wide-character set/get operations for `EL_*` options.
- `el_wline()` exposes current line info.
- `el_source()` reads and parses editrc-style configuration files.
- `el_resize()` handles terminal resize updates.
- `el_beep()` emits terminal bell.
- `el_editmode()` implements the `edit on/off` command.

Initialization order:
- Stores input/output/error `FILE *` and fd values.
- Sets `el_getenv` to `getenv`.
- Decodes and stores program name as wide string.
- Initializes modules in order: terminal, keymacro, map, tty, chared, search, history, prompt, signal, literal, and read.

Configuration behavior:
- `el_wset()` handles prompts, terminal/editor settings, signal/edit/unbuffered/safe-read flags, bindings, termcap commands, tty settings, added functions, history backend, file streams, refresh, word characters, custom getenv, resize callbacks, and alias callbacks.
- `el_wget()` retrieves supported prompt/editor/signal/edit/terminal/input/clientdata/file/wordchars/getenv settings.

Security and config loading:
- `el_source(NULL)` refuses to source files when `issetugid()` reports a set-id context.
- It uses `EDITRC` if set, otherwise `$HOME/.editrc`, skips empty/comment lines, decodes to wide strings, and passes commands to `parse_line()`.

Risks and notes:
- Module initialization return values are not all checked; tty failure sets `NO_TTY`.
- `el_reset()` always calls `tty_cookedmode()` then `ch_reset()`.
- The varargs API requires exact argument types matching `histedit.h`.
