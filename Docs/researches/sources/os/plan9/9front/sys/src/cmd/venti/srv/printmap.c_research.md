# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/printmap.c

`printmap` is a minimal command that loads a Venti config and prints the main index map with `printindex()`. It supports a `-B` option for parity with other tools but does not use the parsed cache size.

The command sets read-only mode unless a never-enabled `fix` variable changes, so it is intended as a non-mutating metadata display utility. Its output depends on the shared print routines rather than local formatting logic.
