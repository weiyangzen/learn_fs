# File Research: sources/os/plan9/9front/sys/src/cmd/mk/var.c

Provides variable get/set/dump helpers and shell variable-name scanning.

Key behavior:
- `getvar()` and `setvar()` read/write `S_VAR` symbol entries, freeing old word lists on set.
- `dumpv()` prints all variables for parse debugging.
- `shname()` returns the end of a shell/mk variable name according to `WORDCHR`.

Important dependencies: `mk.h`, `symlook`, `symtraverse`, `delword`.

Notable risks:
- Variable values are `Word` lists, so callers must honor ownership when setting.
