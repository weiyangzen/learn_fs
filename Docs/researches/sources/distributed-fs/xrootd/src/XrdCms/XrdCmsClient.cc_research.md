# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsClient.cc

## Purpose
Provides the ABI-compatible default CMS client factory used when no external CMS client plugin is loaded.

## Important APIs, Types, and Functions
Defines `XrdCms::GetDefaultClient(XrdSysLogger*, int opMode, int myPort)`. It returns `XrdCmsFinderRMT` for redirector mode, `XrdCmsFinderTRG` for target/server mode, or null for unsupported mode combinations.

## Control Flow
The factory checks `opMode` flags in priority order: `IsRedir` first, then `IsTarget`. Construction arguments are passed through to the selected finder class.

## State and Persistence Behavior
No persistent state. It allocates a new client object for the caller, which owns the returned pointer.

## Dependencies and Integration Points
Depends on `XrdCmsClient.hh` and `XrdCmsFinder.hh`. It is part of the CMS plugin/client instantiation boundary described in the header.

## Risks and Edge Cases
If both redirector and target flags are set, redirector wins. Null return on unsupported mode must be handled by caller initialization. Allocation failures are not locally caught.

## Test Signals
Tests should verify opMode-to-class selection, null result for no recognized role, and ABI linkage for the factory function.
