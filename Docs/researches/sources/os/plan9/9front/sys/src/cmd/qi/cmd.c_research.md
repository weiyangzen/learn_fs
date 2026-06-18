# File Research: sources/os/plan9/9front/sys/src/cmd/qi/cmd.c

Interactive debugger command parser for `qi`.

Key responsibilities:
- Parses expressions and symbols via `numsym`/`expr`.
- Supports colon commands for breakpoints, delete, run, continue, and step.
- Supports dollar commands for stack traces, breakpoint listing, registers, quit, tracing modes, and instruction/memory summaries.
- `pfmt` formats memory or scalar values in many Plan 9 debugger styles, including disassembly via `machdata->das`.
- `quesie` implements memory examination commands.
- `setreg` writes selected CPU registers from evaluated expressions.
- `cmd` is the REPL loop, including last-command repetition and interrupt notification handling.

Dependencies and coupling:
- Uses `bioout`, `bin`, `run`, `reset`, `initstk`, memory accessors, symbol functions, breakpoints, and register state.
- Uses `setjmp(errjmp)`/`longjmp` recovery path shared with instruction faults.

Filesystem/OS relevance:
- Debugger shell around simulated process state; can indirectly read host stdin and symbol tables.
