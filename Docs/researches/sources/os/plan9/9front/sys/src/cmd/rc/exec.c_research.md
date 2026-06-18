# File Research: sources/os/plan9/9front/sys/src/cmd/rc/exec.c

Core interpreter and entry point for `rc`. It initializes flags, traps, variables, bootstrap code, then dispatches bytecode through `runq`.

Defines the runtime thread stack, word/list stack helpers, redirection stack helpers, status handling, error reporting, and most opcode handlers: assignment, variable expansion, subscripting, glob invocation, conditionals, loops, functions, redirections, here-doc execution, parsing loop, and shell exit/trap behavior.

Important contracts: `thread` frames own copied code vectors; `start()` pushes frames; `Xreturn()` unwinds redirections and frames; `Xrdcmds()` invokes `yyparse()` and starts compiled `codebuf`; redirections are stacked in reverse and later applied by `simple.c`.

Filesystem relevance: implements shell-level file descriptor redirection semantics, temporary here-doc files under `/tmp`, pipe wait status propagation, and command source location reporting.
