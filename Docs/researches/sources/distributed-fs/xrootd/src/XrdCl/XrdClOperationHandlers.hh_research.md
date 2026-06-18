# sources/distributed-fs/xrootd/src/XrdCl/XrdClOperationHandlers.hh

## Purpose

This header provides response-handler adapters used by the operation pipeline DSL. It converts raw XrdCl callbacks into lambdas, packaged tasks, futures, single-xattr callbacks, extended-open callbacks, and raw forwarding handlers.

## Important APIs, Types, And Functions

Key classes are `UnpackXAttrStatus`, `UnpackXAttr`, `FunctionWrapper<Response>`, `FunctionWrapper<void>`, `TaskWrapper<Response, Return>`, `TaskWrapper<void, Return>`, `ExOpenFuncWrapper`, `PipelineException`, `FutureWrapperBase<Response>`, `FutureWrapper<Response>`, `FutureWrapper<void>`, `RawWrapper`, `RespBase<Response>`, `Resp<Response>`, and `Resp<void>`. Helpers `GetResponse<Response>(AnyObject*)` and `GetResponse<Response>(XRootDStatus*, AnyObject*)` extract typed payloads.

## Control Flow

Factories in `Resp` build a `ResponseHandler` from a raw handler pointer/reference, `std::future`, `std::function`, lambda-converted function, or packaged task. On callback, wrappers own and delete `XRootDStatus`, `AnyObject`, and sometimes `HostList` using `unique_ptr`, then call user code with references or fulfill promises. Xattr unpackers convert bulk xattr responses into single-operation responses for APIs that expect one attribute.

## State And Persistence

Wrappers store only transient user functions, tasks, promises, futures, or raw handler pointers. `FutureWrapperBase` records whether a promise was fulfilled and sets an exception in the destructor if not. There is no external persistence.

## Dependencies And Integration Points

It depends on `XrdClFile.hh`, `XrdClCtx.hh`, response types, `ResponseHandler`, `AnyObject`, `HostList`, `std::function`, `std::future`, `std::packaged_task`, and the operation pipeline in `XrdClOperations.hh`. `ExOpenFuncWrapper` integrates with `Ctx<File>` and calls `File::Stat` after open.

## Risks

`RawWrapper` forwards to a non-owned handler, so lifetime must exceed pipeline execution. `UnpackXAttrStatus` forwards error status without deleting `response`; callers rely on downstream ownership. `UnpackXAttr` deletes the extracted vector manually after resetting the response object, which depends on `AnyObject` ownership semantics. Function wrappers default-construct dummy responses on errors, requiring `Response` to be default-constructible. `ExOpenFuncWrapper` does not use the status returned by `f->Stat(false, info)` before dereferencing `info`, which is risky on stat failure.

## Test Signals

Tests should cover lambda, future, packaged task, raw handler, void response, non-void response, error response, missing response object, xattr single/bulk adapters, promise exception on abandoned future wrapper, extended-open stat success/failure, and handler lifetime under pipeline replacement/repeat paths.
