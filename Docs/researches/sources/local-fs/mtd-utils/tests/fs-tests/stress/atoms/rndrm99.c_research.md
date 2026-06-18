# File Research: sources/local-fs/mtd-utils/tests/fs-tests/stress/atoms/rndrm99.c

## Purpose
Instrumented variant of `rndrm00` that reports operation counts and long syscall delays.

## Key Elements
Maintains counters for files/directories created/removed and net size, wraps operations with `gettimeofday()` timing, logs any operation taking over 8 seconds, and prints periodic stats every 2000 loop iterations during growth/shrink phases.

## Dependencies
Uses POSIX file/dir APIs, timing APIs, and shared cleanup/random helpers.

## Behavior/Risks
Verbose diagnostic stress test. It duplicates some helper logic locally to add timing, and like `rndrm00` can intentionally fill the filesystem.
