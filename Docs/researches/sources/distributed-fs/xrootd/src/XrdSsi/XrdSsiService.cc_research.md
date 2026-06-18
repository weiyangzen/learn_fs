# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiService.cc

## Purpose
`XrdSsiService.cc` provides the global SSI provider pointer and the default implementation of `XrdSsiService::Prepare`.

## Important APIs and Functions
The file defines `XrdSsi::Provider = 0`. `XrdSsiService::Prepare(XrdSsiErrInfo&, const XrdSsiResource&)` asks the provider whether the resource exists and returns success for any status other than `notPresent`.

## Control Flow
When a derived service does not override `Prepare`, the SSI server can use this default path to validate resource availability. If `Provider` is set and `QueryResource(rName)` reports present or pending, preparation succeeds; otherwise `eInfo` is set to `"Resource not available."` with `ENOENT`.

## State and Persistence
Only the process-global provider pointer is stored. It is initialized during SSI configuration and is not persisted.

## Dependencies and Integration Points
The file depends on `XrdSsiProvider.hh` and `XrdSsiService.hh`. `XrdSsiSfsConfig::ConfigSvc` assigns `Provider`, while `XrdSsiSfs` and `XrdSsiStat` also query it for locate/stat behavior.

## Risks and Test Signals
The default is intentionally simple and treats pending resources as acceptable. Tests should cover null provider, provider returning present, pending, and not-present, and correct `ENOENT` propagation. Integration tests should verify services that need authorization or redirection override `Prepare`.
