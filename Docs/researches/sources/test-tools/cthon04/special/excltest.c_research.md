# sources/test-tools/cthon04/special/excltest.c

## Purpose
tests whether `O_CREAT | O_EXCL` rejects duplicate creation after the first successful open.

## Important APIs, Types, and Functions
`main()` accepts optional count, uses `open()`, `unlink()`, `errno`, and expects `EEXIST` after pass zero.

## Control Flow and State
It unlinks `exctest.file`, loops count times, requires the first create to succeed and all later creates to fail with `EEXIST`.

## Persistence and Dependencies
persistent state is one scratch file that is not explicitly unlinked at success in this small test. Dependencies: POSIX open flags or platform-specific file headers.

## Integration Points, Risks, and Test Signals
Integration is exclusive-create validation. Risks are leaked `exctest.file`, permissions/umask influence, and missing close on created descriptors. Signal is `EEXIST` on every duplicate attempt.
