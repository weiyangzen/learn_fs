# sources/storage-engines/rocksdb/env/fs_on_demand.h

## Purpose
Declares `OnDemandFileSystem`, a `FileSystemWrapper` that presents a local RocksDB directory backed by a remote/source directory, linking immutable table files on demand and reading mutable metadata remotely. Also declares `OnDemandSequentialFile`, which reopens appendable remote sequential files after EOF.

## Important APIs and Types
- `OnDemandFileSystem` overrides sequential/random/writable file creation, directory creation, existence, children listing, attributes listing, and file-size lookup.
- `ReuseWritableFile` is explicitly unsupported.
- Private helpers `CheckPathAndAdjust` and `LookupFileType` drive path mapping and file-type policy.
- `OnDemandSequentialFile : FSSequentialFile` wraps a sequential file and overrides `Read`, `Skip`, direct-I/O metadata, `InvalidateCache`, `PositionedRead`, and `GetTemperature`.
- `NewOnDemandFileSystem` is the public factory.

## Control Flow
The header establishes a policy split: appendable/renameable RocksDB files are read from remote storage; SST/table files are linked locally; writable creation is only expected for info logs. `OnDemandSequentialFile` tracks `eof_` and `offset_`; after a short read marks EOF, the next read can reopen and skip back to the last offset.

## State and Persistence
`OnDemandFileSystem` stores immutable remote and local root strings. `OnDemandSequentialFile` owns the current inner file and stores a non-owning pointer to its `OnDemandFileSystem`, copied `FileOptions`, remote path, EOF flag, and logical offset. Persistent changes are performed by the `.cc` implementation through link and write operations on the target filesystem.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h` and RocksDB file type conventions. It integrates with read-only or follower DB workflows where a local directory should lazily materialize immutable SSTs while reading mutable manifest/current/log state remotely.

## Risks and Edge Cases
- The sequential wrapper stores a raw pointer to `OnDemandFileSystem`; it assumes the filesystem wrapper outlives any open file.
- `InvalidateCache` and `PositionedRead` are unsupported on `OnDemandSequentialFile`, which may surprise generic sequential-file users that expect positioned reads.
- The design comment notes future mirroring of read-in-place files is not implemented, so local diagnostic directories may be incomplete.

## Test Signals
No direct tests are present. Header-level behavior should be validated through DB open/recovery scenarios plus focused filesystem tests for unsupported APIs and file lifetime assumptions.
