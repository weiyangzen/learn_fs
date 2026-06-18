# sources/test-tools/cthon04/special/holey.c

## Purpose
creates a sparse file with alternating patterned data and holes, then verifies that data regions keep their pattern and hole regions read as zeroes.

## Important APIs, Types, and Functions
`main()` owns argument parsing, `Debug`, file constants, `MIN`, `L_INCR`, and buffer pattern generation.

## Control Flow and State
The program creates/reopens a file, writes data chunks and advances with `lseek()` for holes until `filesz` is reached, rewinds, optionally reopens read-only on BSD, then reads every data and hole span, checking integer patterns and zero-filled holes.

## Persistence and Dependencies
persistent state is `holeyfile`/`holefile` or a supplied file, intentionally left unless caller cleanup removes it. Dependencies: POSIX sparse-file semantics, `lseek`, `read`, `write`, `umask`, and binary open mode on DOS/Win.

## Integration Points, Risks, and Test Signals
Integration is sparse-file NFS validation. Risks include alignment assumptions when reading integers from char buffers, platform-specific hole size, and no final unlink. Signals are `Holey file test ok` and no non-zero hole bytes.
