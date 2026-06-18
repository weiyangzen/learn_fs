# sources/storage-engines/leveldb/db/filename.cc

## Purpose
This file constructs and parses LevelDB-owned file names and atomically updates `CURRENT` to point at the active manifest.

## Important APIs, Types, And Functions
`MakeFileName`, `LogFileName`, `TableFileName`, `SSTTableFileName`, `DescriptorFileName`, `CurrentFileName`, `LockFileName`, `TempFileName`, `InfoLogFileName`, `OldInfoLogFileName`, `ParseFileName`, and `SetCurrentFile` are implemented here.

## Control Flow
Numbered files use six-digit formatting plus suffixes `.log`, `.ldb`, `.sst`, or `.dbtmp`; descriptors use `MANIFEST-%06llu`; fixed names include `CURRENT`, `LOCK`, `LOG`, and `LOG.old`. `ParseFileName` recognizes these forms, consumes decimal numbers without locale-sensitive parsing, rejects trailing junk/overflow, and classifies `.sst` and `.ldb` as table files. `SetCurrentFile` writes the manifest basename plus newline to a temp file, renames it over `CURRENT`, and removes the temp on failure.

## State And Persistence Behavior
File naming defines the DB directory layout. `CURRENT` update is persistence-critical because it selects the active descriptor on reopen. Legacy `.sst` table names are accepted for compatibility, while new table names use `.ldb`.

## Dependencies And Integration Points
It depends on Env, status, `Slice`, `ConsumeDecimalNumber`, and `WriteStringToFileSync`. DB creation, recovery, destruction, compaction, table cache, repair, and utilities all rely on these helpers.

## Risks And Edge Cases
Parsing accepts `0.log` and `0.ldb` even constructors assert positive numbers, because existing or malformed names may be inspected. A failed rename leaves old `CURRENT` in place and removes the temp file. Locale-independent parsing avoids platform surprises.

## Test Signals
`filename_test.cc` validates successful and rejected parses, max uint64 boundary handling, and round trips for every constructor.
