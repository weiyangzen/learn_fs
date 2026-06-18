# File Research: sources/os/plan9/9front/sys/src/lib9p/threadlistensrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for network-listening 9P servers.

## Important Function
- `threadlistensrv`: installs `threadsrvforker` if no forker is set, then calls `listensrv`.

## Dependencies and Interactions
- Thin adapter around `listen.c` and `thread.c`.
