# File Research: sources/os/plan9/9front/sys/src/cmd/p.c

## Role

Implements a simple pager that prints fixed-size chunks and waits for console input between chunks.

## Main Behavior

The default chunk length is 22 lines, with an optional `-N` style argument to change it. Files are printed in order; stdin is used when no files are given.

`printfile` uses Bio buffered I/O, writes lines to stdout without adding an extra newline after the last line in a page, flushes output at page boundaries, then reads a command from `/dev/cons`.

## Commands

`q` or EOF exits. A command starting with `!` runs the rest through `/bin/rc -c`, then returns to the prompt. Any other line advances to the next chunk.
