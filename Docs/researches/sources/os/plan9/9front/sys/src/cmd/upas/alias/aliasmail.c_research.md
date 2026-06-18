# File Research: sources/os/plan9/9front/sys/src/cmd/upas/alias/aliasmail.c

`aliasmail` expands local mail aliases from UPAS alias databases. It lowercases input names, reads system names, selects database files from `namefiles` or `fromfiles`, and translates each requested name.

It searches alias files with support for `#include`, converts `@` addresses to bang format for loop checks, and avoids alias cycles by comparing against local and fully qualified system names. Without a match it emits `local!name`; with `-f` it prints the source system/domain side of the alias instead.

The file mutates argv strings in `mklower()`, which matches old Plan 9 utility style but is worth noting if ported.
