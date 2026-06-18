# File Research: sources/os/plan9/9front/sys/src/lib9p/threadpostsrv.c

## Read Status
Complete: 13 lines read.

## Purpose
Thread-style wrapper for posting a 9P server.

## Important Function
- `threadpostsrv`: installs `threadsrvforker` if needed, then returns `postsrv`.

## Dependencies and Interactions
- Thin adapter around `post.c` and `thread.c`.
