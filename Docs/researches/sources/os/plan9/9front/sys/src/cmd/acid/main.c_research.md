# File Research: sources/os/plan9/9front/sys/src/cmd/acid/main.c

Acid debugger entry point, startup, target attachment, module loading, symbol/map setup, REPL loop, GC, and process-exit handling.

Key responsibilities:
- Parses command-line options for kernel mode, write mode, quiet flag, machine override, and library modules.
- Determines target executable from pid/textfile arguments.
- Initializes formatting, output, keywords, input stack, variables, builtins, machine type, maps, symbols, and register variables.
- Loads standard Acid modules, machine-specific modules, requested modules, and user init hooks.
- Runs optional `acidmap()` and then enters the interactive parse/eval loop.
- Handles target executable/header reading and symbol map setup.
- Provides AST/list allocation and mark-sweep GC.
- Handles fatal/syntax errors, interrupt notes, qid checking, kernel filename inference, and debugger exit cleanup.

Important behavior:
- `attachfiles()` runs under noninteractive error trapping and falls back to default register variables on failure.
- `die()` calls a `dying` hook and prints kill commands for processes in `proclist`.
- `readtext()` supports raw binary mapping when `-m` is given.
- GC marks procs and symbol values, then frees unmarked `Gc` objects from the global allocation chain.
- `system()` infers kernel path from `$cputype` and `$terminal`.

Dependencies:
- Uses Plan 9 `mach` library, parser/lexer/evaluator, builtins, module files under `/sys/lib/acid`, and process-control helpers elsewhere in Acid.

Notable risks:
- Startup has many recoverable `setjmp` regions; initialization failures may silently continue depending on `silent` and phase.
- GC relies on all collectible allocations being linked through `gcl`; ordinary `malloc` allocations must be freed manually.
