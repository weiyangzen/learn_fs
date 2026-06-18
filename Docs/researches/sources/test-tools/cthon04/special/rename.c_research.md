# sources/test-tools/cthon04/special/rename.c

## Purpose
renames a scratch file back and forth `n` times to stress repeated rename operations.

## Important APIs, Types, and Functions
`main()` parses count, creates `rename1`, and loops `rename("rename1","rename2")` then back.

## Control Flow and State
After initial creation, each iteration performs two renames and aborts with the current iteration on failure; cleanup unlinks both possible names.

## Persistence and Dependencies
persistent state is `rename1`/`rename2` only during the run. Dependencies: POSIX `open`, `rename`, `unlink` and legacy platform headers.

## Integration Points, Risks, and Test Signals
Integration is rename operation rate/reliability testing. Risks are fixed scratch names in cwd, a dead `cleanup:` label, and no fsync durability. Signal is completion without perror.
