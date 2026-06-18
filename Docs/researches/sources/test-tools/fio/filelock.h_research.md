# sources/test-tools/fio/filelock.h

## Purpose
`filelock.h` declares fio's filename-based in-process locking API.

## Important APIs, Types, And Functions
The header exposes `fio_lock_file(const char *)`, `fio_trylock_file(const char *)`, `fio_unlock_file(const char *)`, `fio_filelock_init()`, and `fio_filelock_exit()`. It includes `lib/types.h` for `bool`.

## Control Flow
The API requires initialization before use and exit after all locks are released. `fio_lock_file` blocks until the filename lock is acquired. `fio_trylock_file` returns a Boolean indicating trylock failure/success according to the implementation's convention; callers must verify the expected polarity in `filelock.c`. `fio_unlock_file` releases by filename.

## State And Persistence
State is hidden in `filelock.c`; the header exposes no structs. Locks are process-local and non-persistent.

## Dependencies And Integration Points
The API is used by fio file setup and job coordination code that needs cooperative in-process exclusion without kernel file locks.

## Risks
The header does not document the return polarity of `fio_trylock_file`, which is non-obvious from the name alone. It also does not state that matching unlocks are mandatory before `fio_filelock_exit()`.

## Test Signals
Header-level validation is mainly compile coverage. Behavioral tests should exercise the implementation through this public API and document trylock return semantics.
