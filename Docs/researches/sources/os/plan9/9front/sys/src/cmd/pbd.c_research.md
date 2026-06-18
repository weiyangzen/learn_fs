# File Research: sources/os/plan9/9front/sys/src/cmd/pbd.c

## Role

Prints the basename of the current working directory.

## Main Behavior

`main` calls `getwd`, finds the last slash, selects the final path component, falls back to `???` on failure, writes the result to stdout, and exits.

It does not append a newline.
