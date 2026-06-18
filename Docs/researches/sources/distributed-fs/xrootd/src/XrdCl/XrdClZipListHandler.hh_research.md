# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipListHandler.hh

## Purpose
`XrdClZipListHandler.hh` declares `ZipListHandler`, a `ResponseHandler` subclass used to implement ZIP-aware directory listing. It abstracts the multi-step decision of "ordinary directory list or archive list" behind one callback object.

## Important APIs and Types
The `Steps` enum has `STAT`, `OPEN`, `CLOSE`, and `DONE`. The constructor accepts a `URL`, path, listing flags, original response handler, and optional timeout; if no timeout is supplied it reads `RequestTimeout` from `DefaultEnv`. It stores the requested path back into `pUrl`. The override `HandleResponse` is implemented in the `.cc` file.

## Control Flow
The header describes three helper transitions: `DoDirList`, `DoZipOpen`, and `DoZipClose`. The object begins at `STAT`, advances to archive open for non-directory paths, closes after listing, and then forwards a `DirectoryList`.

## State and Persistence
State is per operation and in memory only: URL, listing flags, downstream handler, timeout, start time, result list, unused `File` member, `ZipArchive`, and integer step. The handler's lifetime is intentionally asynchronous and self-deleting.

## Dependencies and Integration Points
The declaration includes XrdCl response, filesystem, file, ZIP archive, constants, and default environment headers. It is likely instantiated by ZIP-aware directory listing code outside this work item.

## Risks and Test Signals
The class stores a raw downstream handler and self-deletes, so lifetime tests are important. The `pFile` member is present but unused in the implementation, which is a maintenance signal. Tests should verify default timeout loading, path rewriting on `URL`, and that every terminal state releases exactly one final response.
