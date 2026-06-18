# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/var.c

Read status: complete, 91 lines.

This file implements `rc` keyword and variable lookup. It maintains a small keyword hash table and the global/local variable hash table used by the interpreter.

Key functions are `hash`, `kenter`, `kinit`, `klook`, `gvlook`, `vlook`, and `setvar`. `kinit` registers language tokens such as `for`, `in`, `while`, `if`, `not`, `switch`, and `fn`. `klook` converts an input word token into a keyword token when appropriate.

`gvlook` interns global variables into `gvar`; `vlook` first searches `runq->local` and then falls back to globals. `setvar` replaces an existing word list and marks the variable changed.

Filesystem relevance: no direct filesystem logic, but variable state drives path lookup, environment export, and shell command execution.
