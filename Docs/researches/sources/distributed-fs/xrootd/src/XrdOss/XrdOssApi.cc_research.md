# sources/distributed-fs/xrootd/src/XrdOss/XrdOssApi.cc

## Purpose

`XrdOssApi.cc` implements the default OSS storage-system entry points, plugin loading, initialization, local/remote path translation, directory operations, file open/read/write/stat/close operations, clone support, memory mapping, compression hooks, cache accounting, and basic filesystem mutation helpers.

## Important APIs, Types, and Functions

Top-level globals are `XrdOssSS`, `OssEroute`, and `OssTrace`. Exported factory functions are `XrdOssGetSS` and `XrdOssDefaultSS`. Implemented `XrdOssSys` methods in this file include `Init`, `Lfn2Pfn`, `GenLocalPath`, `GenRemotePath`, `Chmod`, `Mkdir`, `Mkpath`, `Stats`, and `Truncate`. Implemented `XrdOssDir` methods include `Opendir`, `Readdir`, `StatRet`, `Close`, and `Fctl`. Implemented `XrdOssFile` methods include clone variants, `Open`, `Close`, preread `Read`, byte `Read`, `ReadV`, `ReadRaw`, `Write`, `Fchmod`, `Fctl`, `Flush`, `Fstat`, `Fsync`, `getMmap`, `isCompressed`, `Ftruncate`, and private `Open_ufs`.

## Control Flow

`XrdOssGetSS()` verifies version compatibility, initializes default OSS when no plugin is configured, or loads a plugin and resolves the V2 then V1 storage-system factory. `XrdOssSys::Init()` configures the default system and stores the global pointer. Path helpers use optional name-to-name mappers. Directory open chooses local directory reading unless staging and remote reading are configured, otherwise delegates to MSS directory hooks. File `Open()` checks path options, applies read-only policy, opens the local file, triggers staging on missing remote files, validates regular-file status, sets cache accounting for write opens, optionally maps memory based on path/xattr flags, and records clone capability. Reads/writes use `pread`/`pwrite`, with vector preread hints and size limits. Close updates cache accounting and recycles memory/compression resources.

## State and Persistence Behavior

`XrdOssSys` holds configuration-derived roots, path lists, mappers, stage commands, cache/stage counters, preread parameters, stat plugin hooks, and version info. `XrdOssFile` owns an FD, optional cache pointer, memory-map object, compression object, file size snapshot, and clone flag. Operations persist by mutating the local filesystem and, for staged paths, by interacting with configured MSS/stage subsystems. Cache accounting is adjusted on truncate, close, and unlink-like flows elsewhere.

## Dependencies and Integration Points

The file integrates with `XrdOucPinLoader` and `XrdSysPlugin` for plugin loading, `XrdOucName2Name` for path mapping, `XrdOssCache`, `XrdOssMio`, optional compression (`oocx_CXFile`), xattrs, stage/MSS helpers, POSIX filesystem APIs, `XrdSysFD`, and OSS trace/error systems. It is the main implementation behind `XrdOss.hh` and `XrdOssApi.hh`.

## Risks and Edge Cases

Plugin ABI compatibility is critical. Path option handling combines staging, remote, read-only, migration, xattr, memory-map, and clone flags, so regressions often appear only under specific config. `Open()` must close FDs on non-regular files and compression attach failures. `Write()` appears to compare `retval == EBADF` after `pwrite` failure instead of `errno == EBADF`, which may be a latent bug in compressed-file error mapping. Vector preread uses global atomic counters and platform-specific fadvise behavior.

## Test Signals

Tests should cover default and plugin factory paths, version mismatch, N2N mapping success/failure, local and staged opens, read-only/force-read-only policy, directory local/MSS reads, `StatRet`, clone/ioctl success and unsupported paths, cache accounting on writes/truncate/close, memory-map xattr flags, compressed read/raw behavior, vector short read failure, and max-size write rejection.
