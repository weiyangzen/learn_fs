# File Research: sources/os/bsd/netbsd-src/lib/libc/thread-stub/__isthreaded.c

## Purpose
Defines libc's global threaded-state flag.

## Key Elements
Initializes `int __isthreaded = 0`.

## Dependencies
Used by reentrant libc stubs and overridden/updated by libpthread integrations.

## Behavior/Risks
Single global state gates abort behavior in thread stubs once real threading is active.
