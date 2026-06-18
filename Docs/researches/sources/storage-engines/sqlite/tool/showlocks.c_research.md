# sources/storage-engines/sqlite/tool/showlocks.c

## Purpose

POSIX advisory-lock inspector for a single file. It enumerates lock ranges over the first two billion bytes and reports lock start, length, owning pid, and read/write lock type.

## Important APIs, control flow, and dependencies

`showLocksInRange()` maintains a dynamically resized pending range list. For each range, it calls `fcntl(fd, F_GETLK, ...)` with a write-lock probe, prints any conflicting lock, then schedules the unlocked subranges before and after that lock. `main()` opens the target file read/write, invokes the range scan over `0..MX_LCK`, prints `no locks` if none are found, and closes the descriptor.

## State, persistence, and integration

The tool modifies no file content but requires POSIX `fcntl()` lock semantics and read/write open permissions. It is useful around SQLite because SQLite's Unix VFS uses advisory byte-range locks on database files and related lock bytes. It does not know SQLite lock-byte names; it reports raw ranges.

## Risks and test signals

Risks include platform limitation to POSIX locking, inability to inspect locks without opening the file read/write, integer truncation in printed offsets, and races as locks change while scanning. Test signals are controlled processes holding read/write byte-range locks, output covering split ranges without duplicates, and no-lock output after lock release.
