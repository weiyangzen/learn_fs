# File Research: sources/os/plan9/9front/sys/src/9/pc/init9.c

## Purpose
Provides a tiny C entry wrapper that adapts the first argument to Plan 9 boot startup.

## Key Elements
Declares `startboot(char*, char**)` and defines `_main(char *argv0)`, which calls `startboot(argv0, &argv0)`.

## Dependencies
Depends on the boot environment supplying `startboot`.

## Behavior/Risks
There is no defensive logic here; it exists solely to shape the initial argument vector expected by the boot code.
