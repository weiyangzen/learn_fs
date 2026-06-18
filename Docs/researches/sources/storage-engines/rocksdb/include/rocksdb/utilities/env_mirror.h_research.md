# sources/storage-engines/rocksdb/include/rocksdb/utilities/env_mirror.h

## Purpose
Defines `EnvMirror`, an `EnvWrapper` that mirrors filesystem operations to two backing `Env`s and asserts matching semantics. It is a validation aid for new environment implementations.

## Important APIs, Types, And Functions
Overrides include file creation/opening, directory operations, existence checks, `GetChildren`, deletion/creation, size and modification-time queries, rename/link, lock, and unlock. `FileLockMirror` stores paired backend locks.

## Control Flow, State, And Persistence
Each operation is invoked on both `a_` and `b_`; statuses and returned metadata are compared with `assert`, and the primary environment's result is returned. Mutating operations are persisted to both environments. Local state is backend pointers plus ownership flags `free_a_` and `free_b_`.

## Dependencies And Integration Points
Depends on `rocksdb/env.h`, `EnvWrapper`, file abstractions, directories, and file locks. It integrates with DB tests and filesystem portability validation.

## Risks And Edge Cases
Mismatch detection relies on `assert`, which can be disabled. Partial side effects can leave backends divergent if one operation succeeds before the other fails. Modification-time comparison allows tolerance but still assumes broadly matching clocks/semantics. Ownership flags can cause leaks or double deletes if misused.

## Test Signals
Inject mismatched statuses, child lists, file sizes, modification times, lock pairs, mirrored file read mismatches, and destructor ownership paths.
