# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpOpen.cc

## Purpose
`XrdClHttpOpOpen.cc` implements `CurlOpenOp`, the HTTP open operation built on stat semantics, plus `CurlPrefetchOpenOp` behavior for full-download open.

## Important APIs and Functions
`CurlOpenOp` derives from `CurlStatOp`. `SetOpenProperties` records effective URL as `LastURL`, optional object size as prefetch size, ETag, and Cache-Control on the `File`. `Success` rejects directories, stores `ContentLength`, and calls `SuccessImpl(false)`. `Fail` treats 404 as success for create/write/delete open flags. `CurlPrefetchOpenOp::Pause` special-cases the first pause to set open properties from the GET response before delegating to read pause behavior.

## Control Flow
Normal open uses HEAD/PROPFIND stat behavior, then populates file properties needed by later `Stat`, `Read`, and prefetch. Full-download open starts a GET; the first pause after headers establishes the same properties and lets `OpenFullDownloadResponseHandler` mark the file open.

## State and Persistence
No remote state is necessarily changed by open, though create-style opens can accept missing objects and later writes create them. File object properties persist in memory for the handle lifetime.

## Dependencies and Integration Points
The operation integrates `File`, `CurlStatOp`, response info, curl effective URL introspection, and open flag semantics. `File::Open` constructs it.

## Risks and Test Signals
Tests should cover directory open rejection, 404 create success, effective URL after redirect, content length property setting, ETag/cache-control propagation, full-download first-pause behavior, and `ReleaseHandle` clearing socket callbacks.
