# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/tc1.c

This is an interactive narrow-character libedit test shell.

Key behavior:
- Initializes locale, signal handlers, history, tokenizer, and an `EditLine` instance.
- Sets vi mode, enables libedit signal handling, installs an escaped prompt, attaches history, and binds tab to a custom directory completion function.
- Rebinds vi command-mode `j`/`k` to line movement rather than history movement.
- Sources user editrc settings with `el_source(el, NULL)`.
- Reads lines with `el_gets()`, tokenizes them with `tok_line()`, stores them in history, and either handles `history` subcommands, passes libedit commands to `el_parse()`, or forks/execs an external command.

Completion:
- `complete()` finds the current word by scanning backward to whitespace, opens `.`, scans directory entries, and inserts the unmatched suffix of the first matching entry.

Signal handling:
- A simple signal handler stores the signal number in `gotsig`; the main loop reports it and calls `el_reset()`.

Risks and notes:
- The test uses direct shell execution via `fork()`/`execvp()`.
- Completion assumes `opendir(".")` succeeds and does not guard against NULL `DIR *`.
- It is a demonstration/test driver, not library code.
