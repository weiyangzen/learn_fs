# File Research: sources/os/plan9/9front/sys/src/lib9p/threadpostsharesrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for posting a shared 9P server.

## Important Function
- `threadpostsharesrv`: installs `threadsrvforker` if needed, then calls `postsharesrv`.

## Dependencies and Interactions
- Thin adapter around `share.c` and `thread.c`.
