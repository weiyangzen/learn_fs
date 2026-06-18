# sources/storage-engines/sqlite/ext/misc/stmtrand.c

## Purpose
Defines `stmtrand([SEED])`, a deterministic pseudo-random SQL function whose sequence is stable for each invocation of a prepared statement and resets with `sqlite3_reset()`.

## Important APIs, Types, And Functions
The `Stmtrand` struct stores two 32-bit generator states. `stmtrandFunc()` implements the generator and statement-local state. `sqlite3_stmtrand_init()` registers arity-one and arity-zero forms.

## Control Flow
On first call within a statement, `stmtrandFunc()` obtains auxdata using a fixed negative key. If absent, it allocates `Stmtrand`, seeds `x` with `seed|1` and `y` with `seed`, and installs it using `sqlite3_set_auxdata()` with `sqlite3_free` as destructor. Each call advances an LFSR-like `x`, advances `y` with a linear congruential step, XORs them, masks to non-negative 31-bit range, and returns an integer.

## State And Persistence Behavior
State is per prepared statement invocation through SQLite auxdata. It is not persisted in the database and is reset when the statement is reset or finalized. Later arguments in the same statement execution are ignored because the first call's auxdata owns the sequence.

## Dependencies And Integration Points
Depends on SQLite scalar function and auxdata APIs. It is intended for repeatable tests that need pseudo-random values inside SQL queries.

## Risks And Edge Cases
The generator is deterministic but not cryptographic. Because auxdata is keyed independently of argument index, the seed is effectively first-use per statement execution. OOM is reported if auxdata allocation or retrieval fails after set.

## Test Signals
Tests should verify identical sequences across resets for the same seed, different seeds produce different sequences, zero-argument behavior, multiple calls within one row/statement advance the sequence, and OOM paths if fault injection is available.
