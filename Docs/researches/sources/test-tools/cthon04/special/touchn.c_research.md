# sources/test-tools/cthon04/special/touchn.c

## Purpose
creates `n` numbered files named `name<n>` down to `name1` as a simple create workload.

## Important APIs, Types, and Functions
`main()` parses count and repeatedly calls `creat()` with a formatted name.

## Control Flow and State
The loop decrements from the requested count, creating and immediately closing each file.

## Persistence and Dependencies
persistent state is all generated `name*` files; no cleanup is performed. Dependencies: POSIX `creat`, `close`, and `../tests.h` for portability.

## Integration Points, Risks, and Test Signals
Integration is create-count workload generation. Risks include fixed names, no close/create error checking, and no cleanup. Signal is exit zero after file creation.
