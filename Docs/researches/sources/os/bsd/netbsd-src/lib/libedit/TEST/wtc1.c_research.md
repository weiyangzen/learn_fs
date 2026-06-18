# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/wtc1.c

This is a wide-character version of the interactive libedit test shell.

Key behavior:
- Initializes locale, wide history (`history_winit()`), wide tokenizer (`tok_winit()`), and `EditLine`.
- Uses `el_wset()`, `el_wgets()`, `el_wline()`, `el_wparse()`, and wide prompt/history/tokenizer APIs.
- Loads history from `.whistory` on startup and saves it on exit.
- Provides a wide-character directory completion function bound to tab.
- Handles `history`, `history clear`, `history load`, and `history save`.
- For external commands, converts the wide input line to multibyte text, tokenizes with the narrow tokenizer, and `execvp()`s the result.

Completion:
- Finds the current wide word, converts it to multibyte with `wctomb()`, compares against directory entries, converts the remaining suffix back to wide characters, and inserts it with `el_winsertstr()`.

Risks and notes:
- `my_wcstombs()` uses a static growable buffer and does not handle `wcstombs()` failure.
- Completion assumes `opendir(".")` succeeds.
- The test mixes wide and narrow tokenizers for process execution.
