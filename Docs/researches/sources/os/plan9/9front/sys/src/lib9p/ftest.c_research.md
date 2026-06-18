# File Research: sources/os/plan9/9front/sys/src/lib9p/ftest.c

## Read Status
Complete: 28 lines read.

## Purpose
Small test/demo program for file tree creation, dumping, and removal.

## Main Responsibilities
- Create an in-memory tree.
- Add directories `hello` and `goodbye`.
- Add files named `world` under each directory.
- Dump the tree, remove one file, then dump again.

## Important Function
- `main`: exercises tree helpers through calls such as `mktree`, `fcreate`, `fdump`, and `fremove`.

## Notes
- This file uses older or wrapper-style names and includes `"9p.h"` rather than `<9p.h>`, so it appears to be a local test harness or historical test rather than core library implementation.
