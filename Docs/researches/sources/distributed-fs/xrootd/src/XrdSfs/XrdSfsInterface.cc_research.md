# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsInterface.cc

## Purpose
Provides default method implementations for the SFS abstract interfaces. These defaults give conservative behavior for optional features, fallback page I/O, vector I/O, and base filesystem feature initialization.

## Important APIs, Types, And Functions
- `XrdSfsDirectory::autoStat()` defaults to `ENOTSUP`.
- `XrdSfsFile::checkpoint()`, `Clone()`, `fctl(v2)`, `pgRead()`, `pgWrite()`, `read(range list)`, `readv()`, `SendData()`, and `writev()` define fallback behavior for optional methods.
- `XrdSfsFileSystem::XrdSfsFileSystem()` initializes `FeatureSet`.
- `XrdSfsFileSystem::chksum()`, `FAttr()`, `FSctl()`, and `gpFile()` provide defaults.

## Control Flow
Most unsupported optional features set `XrdOucErrInfo` to `ENOTSUP` and return `SFS_ERROR`. Page reads call scalar `read()` then compute CRCs with `XrdOucPgrwUtils::csCalc()`. Page writes optionally verify CRCs with `csVer()` when `Verify` is set, then call scalar `write()`. AIO page operations execute synchronously through the scalar page methods, set `aioparm->Result`, and invoke completion callbacks. Vector reads/writes loop over each `XrdOucIOVec` and fail if any scalar operation transfers less than requested.

## State And Persistence
No persistent data is stored here. The filesystem constructor sets `FeatureSet` to `hasPGRW` and adds `hasCHKP` if `getChkPSize()` reports a positive value. File methods use each object's shared `error` reference for error state.

## Dependencies And Integration Points
Depends on `XrdOucPgrwUtils`, `XrdOucCloneSeg`, `XrdSfsAio`, `XrdSfsFlags`, and the SFS interface declarations. These defaults are inherited by all SFS plugins unless overridden, so they are central compatibility behavior for older plugins.

## Risks And Edge Cases
- Default `FSctl()` returns `SFS_OK` without doing anything, unlike many other unsupported operations. Callers must know command-specific semantics.
- Vector I/O treats short reads/writes as `ESPIPE`, which can mask EOF versus storage errors.
- AIO defaults are synchronous despite the async signature.
- Page write verification assumes the checksum vector layout matches offset and length exactly.

## Test Signals
Tests should assert default errors and return codes, page CRC calculation/verification, AIO callback invocation, vector short-transfer failures, `FeatureSet` initialization when checkpoint size is overridden, and no-op `FSctl()` behavior.
