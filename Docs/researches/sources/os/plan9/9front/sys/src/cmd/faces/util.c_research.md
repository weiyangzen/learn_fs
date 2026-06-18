# File Research: sources/os/plan9/9front/sys/src/cmd/faces/util.c

## Purpose
Provides checked allocation helpers for the `faces` program.

## Key Elements
Implements `emalloc`, `erealloc`, and `estrdup`, exiting on allocation failure and tagging allocations/reallocations with caller PCs.

## Dependencies
Uses Plan 9 libc allocation tagging and `exits`.

## Behavior/Risks
Allocation failure is fatal by design. `emalloc` zeroes memory, while `erealloc` does not initialize newly extended bytes.
