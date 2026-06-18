# sources/storage-engines/leveldb/db/filename.h

## Purpose
This header declares LevelDB file type names, filename construction helpers, filename parsing, and `CURRENT` update API.

## Important APIs, Types, And Functions
`FileType` enumerates `kLogFile`, `kDBLockFile`, `kTableFile`, `kDescriptorFile`, `kCurrentFile`, `kTempFile`, and `kInfoLogFile`. The header declares constructors for log/table/legacy SST/descriptor/current/lock/temp/info-log names, `ParseFileName`, and `SetCurrentFile`.

## Control Flow
The header does not implement behavior, but its comments document DB-owned filename forms and that constructors prefix paths with `dbname`.

## State And Persistence Behavior
These declarations represent the stable DB directory contract. `SetCurrentFile` is used when creating or switching manifests and must make `CURRENT` durable enough for recovery.

## Dependencies And Integration Points
It depends on `Slice`, `Status`, port definitions, and forward-declares `Env`. It is included by DB implementation, dump utilities, tests, corruption/fault-injection suites, and repair/version code.

## Risks And Edge Cases
All components must agree on `FileType` classification. Accepting legacy `.sst` files while creating `.ldb` files is important for compatibility. Misparsing can lead to missed live files or unsafe deletion.

## Test Signals
`filename_test.cc` is the direct coverage; `db_test.cc` missing/legacy SST and destroy tests indirectly validate integration.
