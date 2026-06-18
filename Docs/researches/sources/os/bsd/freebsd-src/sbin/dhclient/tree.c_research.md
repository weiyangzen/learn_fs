# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/tree.c

## Purpose
Minimal list-construction helper for parser data structures.

## Main Elements
- `cons(caddr_t car, pair cdr)`: allocates a pair node, stores head/tail pointers, and returns it.

## Dependencies And Integration
Used by `parse_numeric_aggregate()` when parsing variable-length numeric aggregates before converting them into a contiguous byte buffer.

## Risk Notes
Allocation failure is fatal through `error()`. The pair stores raw pointers and ownership is managed by parser callers.
