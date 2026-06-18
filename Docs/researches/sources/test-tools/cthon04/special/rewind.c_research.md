# sources/test-tools/cthon04/special/rewind.c

## Purpose
checks that `ftruncate(fd,0)` after rewinding really resets file length and the next write produces a one-byte file.

## Important APIs, Types, and Functions
`main()` uses an 8192-byte buffer, writes three blocks, `lseek()`s to zero, truncates, writes one byte, and checks `SEEK_END` offset.

## Control Flow and State
It creates `test.file`, writes 24 KiB, rewinds, truncates to zero, writes one byte, seeks to end, and requires offset 1.

## Persistence and Dependencies
state is `test.file`; this program closes but does not unlink it. Dependencies: POSIX `open`, `write`, `lseek`, `ftruncate`, DOS/Win skip path.

## Integration Points, Risks, and Test Signals
Integration is truncate/offset handling. Risks are uninitialized buffer content, leaked scratch file, and no cleanup on failure. Signal is exit zero with final size one.
