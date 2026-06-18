# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileSystemUtils.hh

## Purpose
`XrdClFileSystemUtils.hh` declares utility APIs related to filesystem-wide operations that do not belong directly on `FileSystem`. Its current public role is a space-information helper that can summarize capacity across located storage servers.

## Important APIs, Types, And Functions
`FileSystemUtils` is a namespace-like class with nested `SpaceInfo`. `SpaceInfo` exposes `GetTotal`, `GetFree`, `GetUsed`, and `GetLargestFreeChunk`, with values documented as megabytes. Its data is hidden behind `std::unique_ptr<SpaceInfoImpl>`. `GetSpaceInfo(SpaceInfo *&result, FileSystem *fs, const std::string &path)` is a static function returning `XRootDStatus`.

## Control Flow
The header only declares behavior, but it establishes caller ownership: `GetSpaceInfo` fills a raw output pointer with a heap-allocated `SpaceInfo` when successful. Consumers must delete the result.

## State And Persistence Behavior
`SpaceInfo` is immutable after construction from the public API. PIMPL storage keeps implementation details and data layout out of the header.

## Dependencies And Integration Points
The header depends on XRootD response/status types, `FileSystem`, strings, integers, and memory utilities. It is intended for code that needs high-level capacity data without manually issuing locate and query operations.

## Risks And Test Signals
Tests should verify getter units, result ownership, null or failed `FileSystem` behavior, and ABI stability around the PIMPL. Documentation should stay aligned with implementation if server values are bytes rather than megabytes.
