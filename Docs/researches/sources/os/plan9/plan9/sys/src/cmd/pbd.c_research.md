# File Research: sources/os/plan9/plan9/sys/src/cmd/pbd.c

Tiny utility that prints the basename of the current working directory.

It calls `getwd`, finds the last slash, skips it when appropriate, writes the selected component to stdout, and exits. If `getwd` fails, it prints `???`.

No newline is emitted.
