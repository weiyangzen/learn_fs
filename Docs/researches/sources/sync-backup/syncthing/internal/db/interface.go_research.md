# sources/sync-backup/syncthing/internal/db/interface.go

## Purpose
This file defines Syncthing's database abstraction: lifecycle service, file update/query APIs, block index operations, cleanup, counts, index IDs, virtual mtimes, and a generic key-value store.

## Important APIs, Control Flow, And State
`DBService` extends `suture.Service` with asynchronous maintenance controls. `UpdateOption`, `UpdateOptions`, and `WithSkipBlockIndex` adjust update behavior. `DB` is the main contract: `Update`, `Close`, single-file lookups, global/local/needed iterators, block index maintenance, delete/drop operations, metadata queries, count queries, index ID management, mtime mapping, and embedded `KV`. `KV` provides `GetKV`, `PutKV`, `DeleteKV`, and prefix iteration. Data carriers include `BlockMapEntry`, `KeyValue`, and `FileMetadata`; `FileMetadata` has helpers for mod time, receive-only changes, directories, conflict flags, and invalid flags.

## State And Persistence
This interface describes persisted file index state, block indexes, folder/device metadata, index IDs, mtime mappings, and arbitrary KV data. Concrete implementations include SQLite and legacy migration readers.

## Dependencies And Integration Points
It depends on Go `iter`, `time`, Syncthing config pull order, protocol types, and `suture` service lifecycle. The interface is consumed by the model, scanner, puller, API, migration, metrics wrapper, and observed pending-device/folder database.

## Risks And Test Signals
Iterator APIs require callers to consume the sequence and then call the returned error function; missed error checks can hide database failures. Some iterators return lightweight `FileMetadata` while others return full `FileInfo`, which callers must not confuse. Implementations should share contract tests for missing folders, iterator early termination, sequence ordering, block index behavior, and `WithSkipBlockIndex`.
