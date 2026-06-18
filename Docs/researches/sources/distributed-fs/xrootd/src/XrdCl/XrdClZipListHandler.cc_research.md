# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipListHandler.cc

## Purpose
`XrdClZipListHandler.cc` implements `ZipListHandler`, an asynchronous response handler that lets `DirList` with the ZIP flag treat a regular ZIP file as a directory while still delegating real directories to normal filesystem listing.

## Important APIs and Functions
`HandleResponse` owns the state machine. `DoDirList` retries an ordinary `FileSystem::DirList` after removing `DirListFlags::Zip`. `DoZipOpen` opens the URL with `ZipArchive::OpenArchive`. `DoZipClose` closes the archive after `ZipArchive::List` has produced a `DirectoryList`.

## Control Flow
The first callback corresponds to a stat operation. If stat says the URL is a directory, `DoDirList` forwards listing to a new `FileSystem` and marks the handler done. Otherwise it opens the URL as a ZIP archive. After `OPEN`, the handler calls `pZip.List`, stores the returned `DirectoryList`, and closes the archive. After `CLOSE`, it packages the directory list into an `AnyObject` and forwards success to the original handler. Any error is forwarded directly, and the handler deletes itself once done.

## State and Persistence
The object is self-owned and deletes itself after the asynchronous chain completes. It stores URL, flags, original handler, timeout start, current step, an owned directory-list result, a `File`, and a `ZipArchive`. No persistent state is written.

## Dependencies and Integration Points
This file integrates `ZipArchive`, `FileSystem`, `DirectoryList`, `StatInfo`, `XRootDStatus`, and `ResponseHandler`. It is the ZIP-aware listing bridge between regular XrdCl filesystem operations and archive member enumeration.

## Risks and Test Signals
Timeout arithmetic assumes a positive effective timeout and uses wall-clock `time(0)`. The code forwards the original response object on errors, so ownership expectations matter. Tests should cover listing a real directory with the ZIP flag, listing a valid archive, stat/open/list/close failures, timeout between stages, no handler leaks, and avoiding infinite recursion by clearing `DirListFlags::Zip`.
