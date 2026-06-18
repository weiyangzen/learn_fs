# sources/sync-backup/syncthing/internal/db/sqlite/db_test.go

## Purpose
This is the broad integration test suite for the SQLite backend. It validates schema initialization, local/global/need APIs, folder and device drops, concurrency, block GC, path handling, error wrapping, and helper constructors.

## Important APIs and Control Flow
`TestBasics` builds a mixed local/remote folder and then subtests schema version, `GetDeviceFile`, `GetGlobalFile`, local/global/need iterators, counts, folder/device listing, sequences, prefix queries, and sequence-ordered local iteration. Other tests cover prefix range behavior with literal `*`, availability lists, dropping files/folders/devices, reset of device sequence on `DropAllFiles`, `DropFolderDevice`, concurrent updates, updating while iterating needed files, matching files by blocklist hash, blocklist garbage collection, large file block insertion, `wrap` formatting, vector ordering regressions, special path names, and block insertion after syncing a remote file locally.

## State and Persistence Behavior
Tests create temporary main and folder SQLite databases, insert `protocol.FileInfo` rows, rely on triggers for counts, and inspect internal tables for blocklist and block counts. They verify folder isolation, device isolation, sequence persistence, global flag recalculation, and deferred block garbage collection.

## Dependencies and Integration Points
The file depends on `internal/db`, `itererr`, `timeutil`, `build`, `config`, `protocol`, and helpers `genFile`, `genDir`, `genBlocks`, `genBlockHash`, `mustCollect`, and `fiNames`. It is the strongest test signal spanning `db_folderdb.go`, `folderdb_*`, `db_service.go`, and `util.go`.

## Risks and Test Signals
This file protects high-risk behavior: concurrent writes through `updateLock`, iterator/read interaction with updates, huge blocklists chunked below SQLite variable limits, URI-like filesystem paths, and historical vector-ordering bugs. The tests intentionally inspect internal tables in a few places, making them sensitive but useful for persistence regressions.
