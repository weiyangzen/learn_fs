# sources/test-tools/cthon04/special/truncate.c

## Purpose
tests whether extending a file with `ftruncate()` through setattr-like semantics updates visible size correctly.

## Important APIs, Types, and Functions
`main()` uses `creat()`, `ftruncate()`, `stat()`, size checks for 0 and 10 bytes, and cleanup unlink.

## Control Flow and State
It creates `testfile`, truncates to zero and verifies size zero, truncates to ten and verifies size ten, closes, unlinks, and prints success.

## Persistence and Dependencies
state is `testfile` during the run. Dependencies: POSIX `ftruncate`, `stat`, and DOS/Win skip path.

## Integration Points, Risks, and Test Signals
Integration is special truncate/SETATTR validation. Risks are fixed scratch name and only checking size, not hole contents. Signal is `truncate succeeded`.
