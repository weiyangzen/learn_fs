# File Research: sources/local-fs/xfsprogs/db/fuzz.c

## Purpose
Implements expert-mode metadata field fuzzing for xfs_db. It modifies selected on-disk structure fields and writes the containing buffer back.

## Main Interfaces
- Registers expert-only `fuzz` through `fuzz_init()`.
- `fuzz_f()` handles command options `-c` and `-d`, selects the current type print/fuzz handler, and manages verifier override behavior.
- `fuzz_struct()` resolves a field expression, applies a named fuzz verb, writes the current buffer, and prints the resulting field.

## Control Flow
The command refuses read-only mode, missing current type, and types without handlers. Normal fuzzing calls the type pfunc with `DB_FUZZ`. Corrupt/invalid-data modes temporarily replace the buffer write verifier so xfs_db can write intentionally bad metadata either with a bad CRC (`-c`) or with recalculated CRC (`-d`). `fuzz_struct()` parses field paths with `flist`, computes the exact bit range, applies verbs such as `zeroes`, `ones`, `firstbit`, `middlebit`, `lastbit`, `add`, `sub`, and `random`, then calls `write_cur()`.

## Dependencies
Uses bit helpers, field/flist parsing, type pfuncs, IO write and verifier helpers, and the global libxfs initialization flags.

## Risks And Invariants
- Available only in expert mode because it can deliberately corrupt metadata.
- `-c` and `-d` are mutually exclusive.
- `-d` requires a type with a known CRC offset or CRC setter.
- Numeric add/sub only support fields up to 64 bits.
