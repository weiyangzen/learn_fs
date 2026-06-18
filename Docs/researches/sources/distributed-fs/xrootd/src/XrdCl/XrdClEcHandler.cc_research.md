# sources/distributed-fs/xrootd/src/XrdCl/XrdClEcHandler.cc

## Purpose
Implements erasure-coding placement support and URL-parameter parsing for the XrdCl erasure-coded file plugin declared in `XrdClEcHandler.hh`.

## Important APIs, Types, And Functions
`ServerSpaceInfo` tracks data-server free space and export paths. Its important methods are `SelectLocations`, `TryInitExportPaths`, `GetFreeSpace`, `BlindSelect`, `UpdateSpaceInfo`, `Exists`, and `AddServers`. `GetEcHandler(const URL &headnode, const URL &redirurl)` validates `xrdec.*` query parameters and returns an `EcHandler` when the redirect URL describes a supported erasure-coded object.

## Control Flow
`ServerSpaceInfo` initializes `xRatio` from `XrdCl_EC_X_RATIO` or defaults to `1`. `SelectLocations` initializes export paths from `XRDEXPORTS`, adds newly seen online servers, refreshes free-space data every 300 seconds, then either prefers highest-free-space servers or blindly selects known online servers depending on list size and `BlindSelect()`. `GetFreeSpace` sends `QueryCode::Space` for each export path and parses `oss.free=` from the response. `GetEcHandler` requires `xrdec.nbdta`, `xrdec.nbprt`, `xrdec.blksz`, `xrdec.plgr`, `xrdec.objid`, `xrdec.format=1`, and `xrdec.cosc`; optional `dtacgi`, `mdtacgi`, `chdigest`, `nomtfile`, and checksum type alter the resulting `XrdEc::ObjCfg`.

## State And Persistence
`ServerSpaceInfo` stores `ServerList`, `ExportPaths`, `lastUpdateT`, `xRatio`, `initExportPaths`, and a mutex. The information is in-memory and refreshed from server queries. `GetEcHandler` allocates `ObjCfg` and possibly a `CheckSumHelper`; ownership moves into the returned `EcHandler`.

## Dependencies And Integration Points
Uses `FileSystem`, `LocationInfo`, `Buffer`, `XRootDStatus`, `URL`, `Utils::splitString`, `XrdEc::ObjCfg`, and checksum helpers. This file is compiled into `XrdCl` only when `BUILD_XRDEC` is enabled and is reached from redirect/plugin integration in file state handling and plugin management.

## Risks
`GetFreeSpace` parses response strings without checking that `oss.free=` and `&` were found, so malformed server responses can produce invalid substrings. `SelectLocations` manually locks/unlocks and can be fragile under future early returns or exceptions. `GetEcHandler` uses `std::stoul` without catching conversion exceptions. If `CheckSumHelper::Initialize()` fails, the allocated `ObjCfg` is leaked before returning null. Optional xattr/placement vectors must match placement size exactly.

## Test Signals
Tests should cover valid and invalid `xrdec.*` redirect URLs, malformed numeric parameters, `plgr` count mismatches, optional CGI vector mismatches, checksum helper initialization failures, free-space selection with and without `XRDEXPORTS`, stale refresh windows, and malformed space-query responses. Build coverage should include both `BUILD_XRDEC=ON` and `OFF`.
