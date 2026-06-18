# File Research: sources/os/plan9/9front/sys/src/lib9p/rfork.c

## Read Status
Complete: 19 lines read.

## Purpose
Default process-style forker for lib9p servers.

## Main Responsibilities
- Start a function in a new Plan 9 process sharing memory.
- Apply caller-supplied `rfork` flags.
- Fatal out if process creation fails.

## Important Function
- `srvforker`: wraps `rfork(RFPROC|RFMEM|RFNOWAIT|flag)`, runs `fn(arg)` in the child, then exits.

## Dependencies and Interactions
- Used as the default `Srv.forker` by `srv.c`, `post.c`, and `listen.c`.
- Alternative thread-style behavior is supplied by `thread.c`.
