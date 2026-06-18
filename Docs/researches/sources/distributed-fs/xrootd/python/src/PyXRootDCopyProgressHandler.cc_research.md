# sources/distributed-fs/xrootd/python/src/PyXRootDCopyProgressHandler.cc

## Purpose
This source adapts XrdCl copy progress notifications into Python handler method calls.

## Important APIs, Types, and Functions
`BeginJob` calls Python `handler.begin(jobNum, jobTotal, source_url, target_url)`. `EndJob` converts the result `PropertyList` and calls `handler.end(jobNum, result)`. `JobProgress` calls `handler.update(jobNum, bytesProcessed, bytesTotal)`. `ShouldCancel` calls `handler.should_cancel(jobNum)` and returns true only if the result is `True`.

## Control Flow
Each callback acquires the GIL with `PyGILState_Ensure`, checks whether a handler was supplied, performs the Python method call, decrefs the return value, and releases the GIL. `EndJob` additionally converts and decrefs the result object.

## State and Persistence
The handler stores only a borrowed-looking `PyObject *handler` pointer from construction. It persists nothing. The underlying copy operation side effects are outside this file.

## Dependencies and Integration Points
Depends on `PyXRootDCopyProgressHandler.hh`, `Conversions.hh`, and XrdCl property/response types. Used by `CopyProcess::Run`.

## Risks and Test Signals
The constructor does not incref the Python handler, so lifetime depends on `CopyProcess::Run` keeping the argument alive while XrdCl calls back. Python exceptions from handler methods are not printed or propagated here. Tests should cover each callback method, handler absence, cancellation return values, Python exceptions in callbacks, and reference lifetime under long-running copies.
