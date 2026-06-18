# sources/storage-engines/rocksdb/env/fs_on_demand.cc

## Purpose
Implements an on-demand filesystem view for read-only/follower-style RocksDB use. It maps a local destination path to a remote source path. Table files are hard-linked into the local directory when first needed, while appendable or rename-sensitive metadata files such as WAL, MANIFEST, CURRENT, IDENTITY, and OPTIONS are read in place from the remote directory.

## Important APIs and Functions
- `OnDemandFileSystem::CheckPathAndAdjust` rewrites a path prefix from local to remote or remote to local.
- `LookupFileType` parses RocksDB filenames with `ParseFileName`.
- `NewSequentialFile` supports WAL, descriptor, CURRENT, IDENTITY, and OPTIONS files; descriptor files are wrapped in `OnDemandSequentialFile`.
- `NewRandomAccessFile`, `FileExists`, and `GetFileSize` link remote table files locally before opening or sizing them.
- `GetChildren` and `GetChildrenFileAttributes` merge local and remote directory listings.
- `OnDemandSequentialFile::{Read,Skip,use_direct_io,GetRequiredBufferAlignment,GetTemperature}` delegates to the active sequential file while tracking EOF and offset.
- `NewOnDemandFileSystem` constructs the wrapper.

## Control Flow
Operations first validate the RocksDB file type. For local-path inputs, `CheckPathAndAdjust(local_path_, remote_path_, path)` creates the remote equivalent. Directory caches for remote paths are discarded before remote lookups. SST random-access reads check the local file, hard-link from remote on not-found/path-not-found, then open locally. Directory listing reads both sides, rewrites remote names to local names, sorts, and merges with `std::set_union`. `OnDemandSequentialFile::Read` reopens and skips to the saved offset after EOF before retrying reads so distributed filesystems can reveal appended data.

## State and Persistence
Persistent effects are hard links created from remote SSTs to local paths and local info LOG writes. The wrapper stores immutable `remote_path_` and `local_path_`. `OnDemandSequentialFile` stores the current `file_`, `path_`, `file_opts_`, `eof_`, and `offset_`; it reopens the remote file after EOF and advances using `Skip(offset_)`.

## Dependencies and Integration Points
Depends on `file/filename.h` for RocksDB file classification, `rocksdb/types.h`, `rocksdb/file_system.h`, and the wrapped `FileSystem` for all actual I/O. It integrates with read-only DB open/recovery flows that list files, replay manifests, verify SST existence, and read metadata files that can grow remotely.

## Risks and Edge Cases
- `LookupFileType` uses `name.substr(found)` where `found` can be `npos` if the path has no slash; that can throw instead of returning unsupported.
- `CheckPathAndAdjust` performs prefix replacement without a path-component boundary check, so paths like `/local_db2/...` can match `/local_db`.
- Hard linking requires same filesystem support; `LinkFile` failures propagate and can prevent table reads.
- `NewWritableFile` permits only info LOG files and rejects writing if the remote equivalent exists; typo in the error text does not affect behavior.
- `OnDemandSequentialFile::Read` calls `fs_->NewSequentialFile(path_, ...)`, which re-enters file-type and path adjustment logic; this is intentional but recursion-sensitive if wrapper rules change.

## Test Signals
No local tests are listed for `fs_on_demand.cc`. High-value tests would cover SST link-on-existence-check, merged listings with duplicate names, descriptor EOF/reopen behavior, unsupported file types, no-slash paths, and hard-link failure propagation.
