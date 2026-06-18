# File Research: sources/os/plan9/9front/sys/src/lib9p/thread.c

## Read Status
Complete: 11 lines read.

## Purpose
Provides a thread/proc-library forker alternative for lib9p servers.

## Important Function
- `threadsrvforker`: runs a server function with `procrfork`, 32 KiB stack, and caller-supplied flags.

## Dependencies and Interactions
- Used by thread-prefixed wrappers to set `Srv.forker`.
