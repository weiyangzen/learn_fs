# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileSystemOperations.hh

## Purpose
`XrdClFileSystemOperations.hh` provides the pipeline/operation-builder layer for filesystem operations. It wraps `FileSystem` callback APIs in CRTP operation classes compatible with `XrdClOperations.hh`, allowing operations to be composed, timed, and invoked through pipeline handlers instead of manually wiring `ResponseHandler` calls.

## Important APIs, Types, And Functions
`FileSystemOperation<Derived, HasHndl, Response, Args...>` is the base template. It extends `ConcreteOperation`, stores a `Ctx<FileSystem>`, and supports move construction between handler states. Derived templates include `LocateImpl`, `DeepLocateImpl`, `MvImpl`, `QueryImpl`, `TruncateFsImpl`, `RmImpl`, `MkDirImpl`, `RmDirImpl`, `ChModImpl`, `PingImpl`, `StatFsImpl`, `StatVFSImpl`, `ProtocolImpl`, `DirListImpl`, `SendInfoImpl`, `PrepareImpl`, and filesystem xattr operation classes.

Most derived `RunImpl` methods extract arguments from the inherited tuple, compute `timeout = min(pipelineTimeout, this->timeout)`, and forward to the corresponding `FileSystem` async API with the pipeline handler. Factory functions avoid naming collisions with file-level operations for `Truncate`, `Stat`, `SetXAttr`, `GetXAttr`, `DelXAttr`, and `ListXAttr`.

## Control Flow
The operation object is constructed with a `Ctx<FileSystem>` and typed `Arg<>` wrappers. When the pipeline executes it, `RunImpl` invokes the callback API. Single xattr variants build a one-element vector and wrap the downstream handler in `UnpackXAttrStatus` or `UnpackXAttr` so a vector protocol response becomes a scalar pipeline response; if submission fails, the wrapper handler is deleted immediately.

## State And Persistence Behavior
Operation instances store only the filesystem context, operation arguments, and inherited operation timeout/handler state. They do not own persistent protocol state; that remains inside `FileSystem`. Move construction copies the `Ctx<FileSystem>` so operations can transition between no-handler and has-handler states while preserving the target object.

## Dependencies And Integration Points
This header depends on `XrdClFileSystem.hh`, generic operation infrastructure, operation handlers, and `Ctx`. It is tightly coupled to the exact `FileSystem` method signatures and to xattr response unpacking helpers.

## Risks And Test Signals
The repeated timeout expression can accidentally pass `0` or the smaller value in surprising ways if pipeline timeout semantics change, so pipeline tests should cover operation timeout less than, greater than, and equal to pipeline timeout. Single xattr adapters need tests for failure-before-submission to catch handler leaks. Compile-time tests should cover factory overload resolution where names overlap with file-level operations.
