# File Research: sources/os/plan9/9front/sys/src/cmd/rc/simple.c

Executes simple commands and builtins. Resolves function calls, explicit `builtin`, builtins, external programs, and optimized tail `exec`.

Contains redirection application, path search, argv construction, `exec`, function invocation, `cd`, `exit`, `shift`, `eval`, dot-source, flag manipulation, `whatis`, and `wait`.

`execcmds()` creates a small code vector around `Xrdcmds` for parsing command streams. `execdot()` opens scripts through `$path`, sets local `$*` and `$0`, and configures interactive/bootstrap/quiet modes.
