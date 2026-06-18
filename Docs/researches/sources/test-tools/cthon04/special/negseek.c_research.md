# sources/test-tools/cthon04/special/negseek.c

## Purpose
ensures negative seeks are rejected by the filesystem/client path rather than allowing reads from invalid offsets.

## Important APIs, Types, and Functions
`main()` opens the supplied filename read-only with create, loops `lseek()` from 0 down to -9216, and reads after successful seeks.

## Control Flow and State
Any failed `lseek()` or `read()` is treated as expected enough to exit success after cleanup; if all negative seeks and reads succeed, the test exits failure.

## Persistence and Dependencies
state is the temporary named file, removed on both expected-failure and all-success paths. Dependencies: POSIX `lseek`, `read`, and legacy DOS/Win behavior.

## Integration Points, Risks, and Test Signals
Integration is invalid-offset testing. Risks are opening with `O_RDONLY|O_CREAT`, accepting a `read` failure as success even if `lseek` passed, and Windows skip. Signal is early error from negative seek/read with exit 0.
