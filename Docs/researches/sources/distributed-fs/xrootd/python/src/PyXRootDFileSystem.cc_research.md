# sources/distributed-fs/xrootd/python/src/PyXRootDFileSystem.cc

## Purpose
This source implements the Python `FileSystem` object wrapping `XrdCl::FileSystem`, exposing namespace, metadata, query, copy, preparation, remote cat, and xattr operations.

## Important APIs, Types, and Functions
Implemented methods include `Copy`, `Locate`, `DeepLocate`, `Mv`, `Query`, `Truncate`, `Rm`, `MkDir`, `RmDir`, `ChMod`, `Ping`, `Stat`, `StatVFS`, `Protocol`, `DirList`, `SendInfo`, `Prepare`, `GetProperty`, `SetProperty`, `Cat`, `SetXAttr`, `GetXAttr`, `DelXAttr`, and `ListXAttr`.

## Control Flow
Most methods follow the same pattern: parse Python args, create an async handler for callbacks or call XrdCl synchronously with the GIL released, convert `XRootDStatus`, convert response objects when present, and return status alone or `(status, response)`. `Copy` constructs a `CopyProcess`, delegates `AddJob`, `Prepare`, and `Run`, and returns `(status, None)` on prepare failure. `Prepare` validates a list of strings before calling XrdCl prepare. `Cat` builds an XrdCl copy process to `stdio://-` and returns only status.

## State and Persistence
The object owns a parsed `URL` and `XrdCl::FileSystem`. Remote persistent side effects include copies, moves, truncates, removals, directory creation/removal, chmod, prepare requests, and xattr mutations. `Cat` writes remote content to stdout via XrdCl.

## Dependencies and Integration Points
Depends on `PyXRootDFileSystem.hh`, `PyXRootDCopyProcess.hh`, `AsyncResponseHandler.hh`, `Utils.hh`, XrdCl filesystem/copy process, and conversion helpers. It is module-registered as `FileSystem`.

## Risks and Test Signals
`GetProperty` and `SetProperty` have the same borrowed singleton return risk as `File`. Several xattr parse format strings are labelled `set_xattr` even in get/delete/list functions, which affects error messages. `Copy` creates temporary tuples/dicts without obvious decrefs on all paths. Tests should cover sync/async methods, argument validation, returned Python shapes for each response type, copy failure paths, xattr list validation, remote cat behavior, and reference-count checks.
