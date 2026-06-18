# File Research: sources/os/plan9/9front/sys/src/cmd/db/main.c

Purpose: Main loop, argument parsing, fault handling, and error recovery for `db`.

Key behavior:
- Supports `-k` kernel mode, `-w` writable mode, `-I dir` include path, and `-m machine`.
- Accepts optional symbol file and optional pid. If a pid is supplied, it defaults symbol/core files to `/proc/<pid>/text` and `/proc/<pid>/mem`.
- Initializes output, machine/symbol map, dot map, core map, and prints current exception/pc when attached.
- Runs a persistent command loop using `setjmp`/`longjmp` recovery.
- `error()` records a pending message, closes redirected input/output, removes breakpoints, and jumps back to the main loop.
- `fault()` catches Plan 9 interrupt notes, seeks current input to end, and resumes.

Notable details:
- Default symbol file is `8.out`.
- In kernel mode with only a pid and no symbol file, it guesses `/386/9<terminal>` using `$cputype` and `$terminal`.
