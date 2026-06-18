# File Research: sources/os/bsd/netbsd-src/lib/libtelnet/genget.c

## Purpose
Implements generic case-insensitive prefix lookup for command/type tables.

## Main Interfaces
Exports `isprefix`, `genget`, and `Ambiguous`.

## Control Flow And State
`isprefix` returns zero for no match, negative length for exact match, and positive prefix length for partial match. `genget` walks a table where the first field is a name pointer and entries are separated by caller-provided struct length. It returns exact match immediately, a unique prefix match if found, an internal ambiguous sentinel for multiple prefix matches, or null for no match. `Ambiguous` checks for that sentinel.

## Dependencies
Uses ctype and declarations from `misc.h`.

## Risks And Notes
The table layout contract is implicit: the first field must be a `char *` compatible name. The ambiguous sentinel is a static address, not a real table entry.
