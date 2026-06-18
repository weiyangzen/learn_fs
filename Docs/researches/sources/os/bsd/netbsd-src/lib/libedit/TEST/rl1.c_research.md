# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/rl1.c

This is a minimal readline compatibility smoke test.

Behavior:
- Repeatedly calls `readline("hi$")`.
- Adds each returned line to history with `add_history()`.
- Prints `history_length` and the line content.

Integration:
- Includes `<readline/readline.h>`, exercising the compatibility API rather than native `histedit.h`.

Risks and notes:
- Returned lines from `readline()` are not freed in this test.
- `argc`/`argv` are unused.
