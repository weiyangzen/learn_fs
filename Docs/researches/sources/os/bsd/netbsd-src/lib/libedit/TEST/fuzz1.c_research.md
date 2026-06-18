# File Research: sources/os/bsd/netbsd-src/lib/libedit/TEST/fuzz1.c

This is a libFuzzer harness for the readline-compatible history expansion interface.

Behavior:
- Initializes locale and stifles history to 7 entries once.
- Clears history for each fuzz input.
- Splits the fuzz buffer on newline boundaries.
- For each non-empty segment, NUL-terminates it, calls `history_expand()`, and adds successful expansions to history.
- Frees both the expansion and temporary segment.

Integration:
- Includes `<readline/readline.h>` and exercises libedit's readline compatibility layer.
- The file header documents sanitizer/fuzzer build and run commands.

Risks and notes:
- Inputs are byte-oriented and optionally run with `-only_ascii=1`.
- The harness deliberately ignores expansion errors and focuses on memory-safety coverage.
