# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqChkPnt.cc

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqChkPnt.cc` implements XRootD checkpoint requests and checkpoint-wrapped execution of modifying operations. It lets clients create, delete, query, restore, and predeclare checkpoint ranges before writes, paged writes, truncates, or writev operations. The source was read as a complete 302-line file.

## Important APIs, Types, and Functions

`XrdXrootdProtocol::do_ChkPnt()` handles direct checkpoint subcodes: begin maps to `XrdSfsFile::cpCreate`, commit to `cpDelete`, query to `cpQuery`, rollback to `cpRestore`, and `kXR_ckpXeq` delegates to `do_ChkPntXeq()`. `do_ChkPntXeq()` validates an embedded request header, rewrites `Request.header` to the subject request, optionally reads an embedded writev vector, extracts the target file handle, calls SFS checkpoint operations such as `cpWrite` or `cpTrunc`, and then dispatches the real write, pgwrite, truncate, or writev handler.

## Control Flow

Direct checkpoint flow validates the file handle, invokes the requested checkpoint method on the SFS file, returns checkpoint size data for query, and maps errors through `fsError()`. Embedded execution is two-pass for writev: the first pass validates stream ID and payload length, copies the embedded request body, fetches the vector if needed, and may resume after socket reads. The second pass checks the target file, performs a checkpoint range declaration, then calls the underlying operation. For writev, it rejects multi-file checkpoint writev because one checkpoint target is required.

## State and Persistence Behavior

Checkpoint state is stored by the underlying `XrdSfsFile` implementation, not by this file. The handler mutates `Request.header` to represent the embedded operation while setting `requestid` back to `kXR_chkpoint` during checkpoint preparation. For writev, it uses the protocol's `wvInfo` state allocated by `do_WriteV()` and frees it on unsupported multi-file cases. Socket-buffer state can persist across a resume while reading embedded writev arguments.

## Dependencies and Integration Points

The file depends on XProtocol request structs, XrdBuffer, XrdLink, XrdOucErrInfo, XrdSfsInterface, `XrdXrootdFile`, monitoring data, stats, trace macros, `XrdXrootdWVInfo`, and `XrdXrootdXeq.hh`. It integrates with the core write, pgwrite, truncate, and writev implementations in `XrdXrootdXeq.cc` and `XrdXrootdXeqPgrw.cc`, and with SFS file checkpoint support.

## Risks and Edge Cases

Embedded execution mutates global request fields, so every downstream handler must tolerate being called under a checkpoint wrapper. Bad file handles for write and pgwrite require draining or terminating the connection to avoid protocol desynchronization. The error branches for pgwrite/write set `IO.EInfo[0] = SFS_ERROR; IO.EInfo[0] = 0;`, which appears to zero the same slot instead of setting `IO.EInfo[1]`; that should be audited because it can affect the error returned after draining. Multi-file writev is explicitly unsupported. Invalid SFS checkpoint return codes are coerced to logic errors.

## Test Signals

Tests should cover begin, commit, query, rollback, invalid subcodes, invalid file handles, embedded stream-ID mismatch, invalid embedded request length, recursive checkpoint rejection, truncate-with-path rejection, checkpointed write, checkpointed pgwrite, checkpointed truncate-by-handle, single-file checkpointed writev, multi-file writev rejection, resume while reading embedded writev vectors, and SFS failures for `cpWrite`/`cpTrunc` that still require socket draining.
