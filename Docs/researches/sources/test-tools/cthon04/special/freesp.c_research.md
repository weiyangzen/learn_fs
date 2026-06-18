# sources/test-tools/cthon04/special/freesp.c

## Purpose
verifies System V `fcntl(F_FREESP)` truncation semantics after writing several full buffers and a partial buffer.

## Important APIs, Types, and Functions
`main()`, `verify_size()`, `flock_t clear`, `F_FREESP`, `BUFSIZE`, `PARTIAL_BUF`, and `NUMBUFS` are key.

## Control Flow and State
When `F_FREESP` exists, it writes three 8192-byte buffers plus 42 bytes, verifies size, seeks to zero, clears from zero to EOF with `fcntl`, verifies zero length, closes, and unlinks. Without support it prints a skip.

## Persistence and Dependencies
state is `freesp.dat` or a supplied filename plus its file offset. Dependencies: System V file-space APIs, `fcntl`, `lseek`, and POSIX file I/O.

## Integration Points, Risks, and Test Signals
Integration is optional free-space/truncate testing. Risks are non-portability of `F_FREESP`, destructive filename handling, and relying on `lseek` as size. Signals are skip on unsupported platforms or exact size transition to zero.
