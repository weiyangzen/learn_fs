# sources/storage-engines/badger/util.go

## Purpose
This file provides small Badger package utilities for validating LSM level invariants, reserving table file IDs, scanning existing table IDs from a directory, and seeding the package random generator.

## Important APIs, Types, And Functions
`(*levelsController).validate` iterates all `levelHandler`s and wraps validation errors. `(*levelHandler).validate` checks non-L0 tables are sorted and have valid internal key ranges using `y.CompareKeys`, `Smallest`, `Biggest`, and table IDs. `reserveFileID` atomically increments `nextFileID`. `getIDMap` reads a directory and parses table file names via `table.ParseFileID`.

## Control Flow
Validation skips level 0 because L0 may overlap. For higher levels it takes an `RLock`, walks adjacent table pairs, rejects inter-table overlap, and rejects a table whose smallest key sorts after its biggest key. `getIDMap` ignores subdirectories and non-table filenames.

## State And Persistence Behavior
The file reads filesystem directory entries but does not mutate persistent state. File ID reservation mutates the in-memory atomic `nextFileID` counter. Validation observes the current in-memory table list under a read lock.

## Dependencies And Integration Points
It integrates with the table package, LSM level controller/handler structures, Badger key ordering helpers, and logging/error wrapping in `y`. The debug-print helpers are commented out and not active.

## Risks And Edge Cases
Validation depends on all table keys carrying timestamp suffixes acceptable to `y.CompareKeys`. `getIDMap` calls `y.Check`, so directory read errors terminate the process rather than returning an error. Random seeding in `init` introduces package-global nondeterminism for tests that use `math/rand`.

## Test Signals
There is no direct test in this file. Regressions surface through compaction, opening existing tables, or explicit LSM validation callers.
