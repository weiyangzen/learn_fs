# sources/distributed-fs/xrootd/python/src/AsyncResponseHandler.hh

## Purpose
This header implements the generic bridge from asynchronous XrdCl responses to Python callbacks in the XRootD Python extension.

## Important APIs, Types, and Functions
`template<class Type> AsyncResponseHandler` subclasses `XrdCl::ResponseHandler`. It implements `HandleResponseWithHosts`, `HandleResponse`, `ParseResponse`, and `Exit`. `GetHandler<T>(PyObject *callback)` validates and increfs a Python callback through `IsCallable` and returns a new handler instance.

## Control Flow
On callback from XrdCl, the handler first avoids interpreter-finalization deadlock by returning if `Py_IsInitialized()` is false. It acquires the GIL, initializes Python types, converts `XRootDStatus`, converts the typed response from `AnyObject`, optionally converts host lists, constructs callback arguments, determines whether the response is final by checking `suContinue`, invokes the Python callback, releases references, releases the GIL, deletes XrdCl-owned response/status/host objects, and self-deletes on final response. Error paths call `Exit`, which prints Python errors, releases the GIL, and deletes `this`.

## State and Persistence
State is the retained Python callback pointer and GIL state. The handler owns its lifetime after submission to XrdCl and deletes itself after a final response or conversion/callback error. There is no persistence.

## Dependencies and Integration Points
Depends on `PyXRootD.hh`, `Conversions.hh`, `Utils.hh`, and XrdCl response types. It is used by file and filesystem async methods for typed response conversion.

## Risks and Test Signals
The no-interpreter path returns without deleting `status`, `response`, or `hostList`, trading shutdown safety for potential leaks. Callback ownership depends on `IsCallable` incref and final-response decref. Self-deletion is fragile if XrdCl ever reuses the handler after an error. Tests should exercise async callbacks for final and `suContinue` chunked responses, host-list responses, callback exceptions, and interpreter shutdown behavior.
