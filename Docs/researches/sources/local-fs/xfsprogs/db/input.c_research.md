# File Research: sources/local-fs/xfsprogs/db/input.c

## Purpose
Implements xfs_db command input: tokenization, interactive line fetching, optional editline history, nested source files, and command-file execution.

## Main Interfaces
- Registers `source` through `input_init()`.
- Exports `breakline()`, `doneline()`, `fetchline()`, and `pushfile()`.

## Control Flow
`tokenize()` splits input on whitespace while preserving quoted strings and escaped characters. `breakline()` builds a NULL-terminated argv vector. `fetchline_internal()` reads from the current input stream, handles prompts and continuation lines ending in backslash, logs top-level input, and pops exhausted input streams. With editline enabled, stdin uses history and line editing; nested sources still use the internal reader. `source_f()` opens a file, pushes it, and executes its commands immediately until EOF or a command signals done.

## Dependencies
Uses command dispatch, output/logging, signal interrupt state, malloc wrappers, and optional `histedit`.

## Risks And Invariants
- The input stack owns non-stdin file closure on pop.
- Tokenization mutates the input buffer in place.
- `source_f()` diagnostics print `argv[0]` on open failure, which names the command rather than the failed file.
