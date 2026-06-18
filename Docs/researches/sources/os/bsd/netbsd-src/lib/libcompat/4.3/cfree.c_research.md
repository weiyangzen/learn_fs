# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.3/cfree.c

## Purpose
Implements historical `cfree()` compatibility API.

## Behavior
Calls `free(p)`.

## Dependencies
Depends on `<stdlib.h>`.

## Risks And Notes
This exists only for source/binary compatibility with older interfaces.
