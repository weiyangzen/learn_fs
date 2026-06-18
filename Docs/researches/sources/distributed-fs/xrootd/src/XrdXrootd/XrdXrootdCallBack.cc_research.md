# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdCallBack.cc

Purpose: implements asynchronous filesystem callback handling for xrootd operations. It schedules response work away from the filesystem callback thread, then converts SFS callback results into xrootd response packets.

Important APIs and functions: internal `XrdXrootdCBJob::Alloc()` reuses callback jobs from a static free list. `DoIt()` dispatches special close, open, and statx handling, sends success or error responses, calls any nested errinfo callback, deletes or recycles state, and frees close file objects. `DoClose()` validates close results, sends final close responses, and returns the file object for disposal. `DoStatx()` rewrites statx text into xrootd file-type flags. `XrdXrootdCallBack::Done()` schedules a job. `sendError()` handles `SFS_DATAVEC`, `SFS_ERROR`, `SFS_REDIRECT`, stalls, `SFS_DATA`, and unknown SFS results. `sendResp()` and `sendVesp()` send async responses by request id.

Control flow and state: global static pointers to error logger, stats, scheduler, and port are installed by `setVals()`. `XrdOucErrInfo::getErrArg()` carries a packed `XrdXrootdReqID`; for close it is temporarily replaced from the file's saved callback argument.

Dependencies and integration: integrates SFS async callbacks with `XrdXrootdResponse`, `XrdXrootdMonitor::Redirect`, stats counters, scheduler jobs, and file lifecycle. It is initialized from protocol configuration before filesystem callbacks are possible.

Risks and test signals: response correctness depends on `ErrInfo` contents and callback result conventions. Tests should cover async open wait-zero retry, close success and invalid close result, redirect monitoring, vectored data responses, stall responses, missing clients during async send, and cleanup of external errinfo buffers.
