# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/fns.h

Function prototype header for `mk`.

Coverage:
- Declares parser, rule, graph, job, environment, shell, word-list, symbol-table, archive, file-time, and platform functions.
- Exposes constructors like `newarc`, `newbuf`, `newjob`, `newword`.
- Exposes execution functions like `run`, `waitup`, `execsh`, `pipecmd`.
- Exposes utility functions like `Malloc`, `Realloc`, `charin`, `wtos`, `varsub`.

Role:
- Included at the end of `mk.h`, making it the central cross-module interface for the build system.
