# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipOperations.hh

## Purpose
`XrdClZipOperations.hh` adapts `ZipArchive` methods to the generic XrdCl operation pipeline. It provides CRTP operation classes and factory functions so archive open, member open, reads, writes, append, stat, list, close-file, and close-archive can be composed like other XrdCl operations.

## Important APIs and Types
`ZipOperation` derives from `ConcreteOperation` and stores `Ctx<ZipArchive> zip`. Operation classes include `OpenArchiveImpl`, `OpenFileImpl`, `ZipReadImpl`, `ZipReadFromImpl`, `ZipWriteImpl`, `AppendFileImpl`, `CloseFileImpl`, `ZipStatImpl`, `ZipListImpl`, and `CloseArchiveImpl`. Inline factories expose `OpenArchive`, `OpenFile`, `Read`, `ReadFrom`, `Write`, `AppendFile`, `Stat`, `List`, and `CloseArchive`; `CloseFile` is a typedef.

## Control Flow
Each `RunImpl` extracts typed arguments from the operation tuple, computes a timeout as the minimum of pipeline and operation timeout, calls the corresponding `ZipArchive` method, and either lets the archive perform an asynchronous callback or immediately packages synchronous results into `AnyObject`. `OpenFile` and `CloseFile` are synchronous from the archive perspective and manually invoke the pipeline handler on success.

## State and Persistence
The operation wrappers own no archive data beyond the shared `Ctx<ZipArchive>`. Archive persistence and mutable state remain inside `ZipArchive`; these classes preserve pipeline arguments and handler flow.

## Dependencies and Integration Points
This header depends on `XrdClZipArchive.hh`, `XrdClOperations.hh`, `XrdClOperationHandlers.hh`, and `XrdClCtx.hh`. It is the integration layer between archive semantics and the broader XrdCl operation DSL.

## Risks and Test Signals
Timeout min logic can accidentally pass zero or stale operation defaults depending on pipeline usage. `ZipListImpl::ToString` returns `"ZipStat"`, likely a copy/paste observability issue. Tests should cover pipeline chaining, move construction across handler states, synchronous handler invocation, response object ownership, and failure propagation from each archive method.
