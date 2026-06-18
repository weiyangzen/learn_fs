# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileOperations.hh

## Purpose
`XrdClFileOperations.hh` adapts the `XrdCl::File` facade into the XrdCl operation/pipeline framework. It provides small CRTP operation classes and factory functions so file operations can be composed with the workflow operators implemented in `XrdClOperations.hh`, streamed into handlers with `operator>>`, run asynchronously, and chained with common timeout handling. The file is a header-only bridge between user-friendly file pipeline syntax and the concrete async methods in `File`.

## Important APIs, Types, And Functions
`FileOperation<Derived, HasHndl, Response, Arguments...>` is the shared base. It derives from `ConcreteOperation`, stores `Ctx<File> file`, forwards argument wrappers to the concrete operation base, and provides a move constructor that converts between handled and unhandled operation states. The `Ctx<File>` wrapper keeps the target file object accessible across pipeline movement.

The header defines operation implementations for `Open`, `Read`, `PgRead`, `PgWrite`, `Close`, `Stat`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, `WriteV`, `Fcntl`, `Visa`, and extended attributes. Each implementation defines argument indexes, `ToString()`, and a protected `RunImpl(PipelineHandler *, time_t)` that extracts `Arg<T>` values from `this->args`, computes the effective timeout, and delegates to the matching async `File` method.

Factory functions return unhandled operations, typically with `.Timeout(timeout)` applied: `Open`, `Read`, `PgRead`, `RdWithRsp<ChunkInfo/PageInfo>`, `PgWrite`, `Close`, `Stat`, `Write`, `Sync`, `Truncate`, `VectorRead`, `VectorWrite`, and `WriteV`. `Fcntl` and `Visa` are exposed as typedefs to their unhandled implementation types. Xattr factories overload `SetXAttr`, `GetXAttr`, and `DelXAttr` for single-name and bulk vector forms, and `ListXAttr` creates the list operation.

`OpenImpl` has an extended response factory, `ExResp`, that adds handler creation for `std::function<void(XRootDStatus&, StatInfo&)>` while retaining the base `Resp<void>` overloads. It wraps such callbacks in `ExOpenFuncWrapper`, allowing open pipelines to observe the opened file's stat information. Single-xattr operations use `UnpackXAttrStatus` and `UnpackXAttr` from `XrdClOperationHandlers.hh` to convert vector/bulk file responses into scalar pipeline responses.

## Control Flow
A typical operation is built by a factory, optionally gets a timeout, then is converted to a handled operation by `operator>>` or another pipeline composition primitive. When the workflow engine runs it, `ConcreteOperation` calls the operation's `RunImpl`. `RunImpl` extracts stable values from the stored tuple and invokes the corresponding async `File` call with the pipeline handler. The pipeline handler receives the eventual XRootD callback and advances the workflow or completes the final promise.

Timeout control is consistent throughout the file: `RunImpl` sets `timeout` to the smaller of `pipelineTimeout` and the operation timeout. That embeds operation-level deadlines under an outer pipeline budget. Operations that return data use response template types such as `Resp<ChunkInfo>`, `Resp<PageInfo>`, `Resp<VectorReadInfo>`, `Resp<Buffer>`, `Resp<std::vector<XAttr>>`, or `Resp<std::vector<XAttrStatus>>`; status-only operations use `Resp<void>`.

The xattr single-item flow is slightly more involved. `SetXAttrImpl` wraps a name/value pair in a `std::vector<xattr_t>`, allocates `UnpackXAttrStatus`, and deletes the wrapper if submission fails. `GetXAttrImpl` wraps a single name in a vector, allocates `UnpackXAttr`, and deletes it on immediate failure. `DelXAttrImpl` follows the same pattern as set. Bulk xattr operations pass the vectors directly and return bulk response types.

## State And Persistence Behavior
Operation objects are transient and once-use-only by inheritance from `Operation`. They persist only enough state to run: a `Ctx<File>`, a tuple of `Arg<T>` values, an optional timeout, and, after handler binding, a pipeline handler. Moving an operation invalidates the source operation in the base framework. No file data is stored in this layer; all durable effects happen through the underlying `File` methods.

The operation layer does affect lifetime expectations. Buffer and argument wrappers must remain valid according to how `Arg<T>` stores them, and `Ctx<File>` must refer to a usable file. `WriteVImpl` copies a `std::vector<iovec>` into a stack array before invoking `File::WriteV`; the underlying async write must not depend on that stack array after the call unless the deeper `FileStateHandler` copies it immediately. Xattr unpack wrappers allocate helper handlers and hand ownership to the async response path on successful submission.

## Dependencies And Integration Points
This header includes `XrdClFile.hh`, `XrdClOperations.hh`, `XrdClOperationHandlers.hh`, and `XrdClCtx.hh`. It depends on the operation framework for `Operation`, `ConcreteOperation`, `PipelineHandler`, `Resp`, `Arg`, timeout propagation, move-only operation validity, and stream/pipeline composition. It depends on `File` for the actual network/protocol work and on response wrapper helpers for scalar xattr callback adaptation.

It is the pipeline counterpart of the public `File` API. Any signature mismatch with `XrdClFile.hh` or behavior change in `File` propagates here. `RdWithRsp` integrates page and chunk reads through a response-type trait, allowing generic code to select `ReadImpl` or `PgReadImpl` by expected response type. Name clashes with filesystem operations are handled by comments and specific factory names, while operation `ToString()` values are used for workflow diagnostics.

## Risks And Edge Cases
The effective timeout expression uses `pipelineTimeout < this->timeout ? pipelineTimeout : this->timeout`; if either value can be zero to mean "default/no explicit timeout", this min operation may accidentally choose zero instead of a nonzero bound, depending on framework semantics. That should be verified against `XrdClOperationTimeout.hh`.

`WriteVImpl` uses a variable-length stack array `iovec iov[iovcnt]`, which is not standard C++ and can be risky for empty or very large vectors. It also passes a stack-backed array into an async API. This is only safe if the callee copies synchronously before returning. `PgWriteImpl` uses `Arg<void*>` while `File::PgWrite` expects `const void *`; the implicit conversion is fine for non-const buffers but weakens const-correctness at the pipeline API. Several `ToString()` methods return implementation names such as `SetXAttrImpl`, which may be less stable for user-facing diagnostics than operation names.

Single-xattr unpack handlers assume response shapes produced by bulk xattr file calls. Old servers may return non-OK statuses or no response, and the wrappers must avoid leaks and null dereferences. Handler ownership is subtle: helpers are deleted only on immediate submission failure; on success the callback path must eventually delete or own them according to pipeline conventions.

## Test Signals
Tests should construct each factory and verify `ToString`, argument forwarding, timeout propagation, and handler response type. Pipeline tests should cover normal chaining, `operator>>` conversion from unhandled to handled operations, moving operations once, and rejection of using moved-from operations via the base framework. File-level integration tests should assert that each `RunImpl` invokes the expected async `File` method with the extracted arguments.

Specific regression tests should cover `OpenImpl` custom callback overloads, `RdWithRsp<ChunkInfo>` versus `RdWithRsp<PageInfo>`, single and bulk xattr success/error paths, deletion of unpack wrappers on immediate failure, zero and nonzero pipeline/operation timeout combinations, empty and large `WriteV` vectors, and async safety of iovec lifetimes. Compile tests should run under strict standard C++ flags to catch the variable-length array and constness issues.
