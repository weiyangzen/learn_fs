# sources/test-tools/cthon04/special/op_unlk.c

## Purpose
tests that an open file continues to support I/O after its directory entry is unlinked.

## Important APIs, Types, and Functions
`main()`, `xxit()`, temp name creation, `unlink()`, `write()`, `lseek()`, `read()`, close/unlink error checks, and `CHMOD_RW` are key.

## Control Flow and State
It opens a temp file, unlinks it while open on Unix, writes/reads a fixed buffer through the descriptor, expects a second unlink to fail with `ENOENT` or `EACCES`, closes, and expects a second close to fail.

## Persistence and Dependencies
state is the open-but-unlinked inode and temp name; cleanup diverges for Windows. Dependencies: Unix open-unlink semantics and DOS/Win path restrictions.

## Integration Points, Risks, and Test Signals
Integration is open-unlinked-file validation. Risks include shelling out to `ls`, `tempnam()`, platform-specific expected errno, and possible leftover files on error. Signals are data compare ok, expected second unlink failure, and expected second close failure.
