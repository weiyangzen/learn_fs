# File Research: sources/os/plan9/9front/sys/src/lib9p/threadsrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for running a 9P server.

## Important Function
- `threadsrv`: installs `threadsrvforker` if needed, then calls `srv`.

## Dependencies and Interactions
- Thin adapter around `srv.c` and `thread.c`.
