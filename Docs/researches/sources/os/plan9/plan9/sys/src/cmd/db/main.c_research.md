# File Research: sources/os/plan9/plan9/sys/src/cmd/db/main.c

Main command loop, argument handling, and error/interrupt recovery for Plan 9 `db`.

Key responsibilities:
- Parses flags:
  - `-k` kernel mode
  - `-w` open core writable
  - `-I dir` include/source path
  - `-m machine` machine override.
- Determines `symfil` and `corfil` from optional symbol file and optional pid.
- For a pid without explicit symfile:
  - non-kernel uses `/proc/<pid>/text`.
  - kernel mode guesses kernel path from `$cputype` and `$terminal`.
  - core file is `/proc/<pid>/mem`.
- Initializes output, symbols, `dotmap`, machine selection, and optional core mapping.
- Main loop:
  - prints pending error messages.
  - handles interrupts.
  - reads a command.
  - exits on EOF from stdin.
  - executes command and enforces newline.
- `done()` exits, ending active process control if needed.
- `error()` stores an error message, closes input/output, flushes, deletes breakpoints, and longjmps to the main loop.
- `errors()` formats a two-part error.
- `fault()` handles interrupt notes by seeking current input to EOF and setting `mkfault`.

Important interactions:
- Uses `setjmp`/`longjmp` for debugger error recovery.
- Uses setup functions (`setsym`, `setcor`, `dumbmap`) and process-control cleanup (`delbp`, `endpcs`) declared in `fns.h`.

Research notes:
- `xargc` is retained as a global compatibility variable.
- If `-m` names an unknown machine, it reports but continues with default machine.
