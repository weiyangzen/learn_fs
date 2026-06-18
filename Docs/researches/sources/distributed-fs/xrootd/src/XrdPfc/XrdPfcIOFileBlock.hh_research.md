# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcIOFileBlock.hh

## Purpose
Declares `IOFileBlock`, the block-splitting cache IO adapter. It is intended for configurations that store a logical remote object as multiple local cache files, each backed by a shared `File`.

## Important APIs, Types, and Functions
- Overrides `ioActive`, `DetachFinalize`, `Read`, `Fstat`, `FSize`, and `Update`.
- `m_blocksize`: logical split size.
- `m_blocks`: map from block index to lazily created `File*`.
- `m_localStat`, `m_info`, and `m_info_file`: logical file stat/metadata state.
- Private helpers parse block size from path, initialize local stat, create block files, and close the top-level info file.

## Control Flow
Callers use the same XRootD cache IO API as `IOFile`, but reads are internally divided into per-block `File` reads. Update and detach walk all block files under a mutex.

## State and Persistence Behavior
The adapter owns a logical `.cinfo` plus a runtime map of block files. Each block file has its own persistence through `File`. The top-level stat is cached in `m_localStat`.

## Dependencies and Integration Points
Depends on `XrdOucCache`, `XrdPfcIO`, `Info`, and `File` implementation details. It integrates with `Cache::GetFile` using generated block-suffixed filenames.

## Risks and Test Signals
The class is older and has comments questioning mutex necessity and suggesting `IOFileBlock` should be ditched. Tests should focus on thread safety of `m_blocks`, logical stat correctness, and compatibility with `File` offset handling.
