# File Research: sources/os/plan9/9front/sys/src/lib9p/threadpostmountsrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for posting and mounting a 9P server.

## Important Function
- `threadpostmountsrv`: installs `threadsrvforker` if needed, then calls `postmountsrv`.

## Dependencies and Interactions
- Thin adapter around `mount.c` and `thread.c`.
