# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/simple.c

Execution of simple commands and rc builtins.

Main command path:
- `Xsimple()` glob-expands argv, resolves functions, `builtin`, builtins table, optimized final `exec`, or forks external commands.
- `doredir()` applies deferred redirections.
- `searchpath()` chooses path lookup or direct execution.
- `execexec()` replaces shell execution path with external command.
- `execfunc()` starts a function with local `$*`.

Builtins implemented:
- `cd` with `cdpath` and `/dev/wdir` update for interactive shells.
- `exit`.
- `shift`.
- `eval`.
- `.` for sourcing files with local `$0` and `$*`.
- `flag` to inspect/toggle shell flags.
- `whatis` for variables, functions, builtins, and path lookup.
- `wait`.

Helpers:
- `exitnext()` optimizes commands followed only by exit.
- `dochdir()`, `appfile()`, `octal()`, `mapfd()`, `execcmds()`.

Risk/notes:
- `execdot()` carefully transfers caller argv list into sourced command frame.
- `execwhatis()` writes through mapped stdout but notes it should ideally fork first.
- `mapfd()` computes effective fd mapping from pending redirections.
