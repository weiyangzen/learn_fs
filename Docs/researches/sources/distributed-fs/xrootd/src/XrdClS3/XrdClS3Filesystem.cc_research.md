# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3Filesystem.cc

## Purpose
Implements an S3 filesystem plugin that maps XRootD filesystem operations onto HTTPS/S3 operations. It supports directory listing through S3 `ListObjectsV2`, stat fallback from object to pseudo-directory, mkdir/rmdir through sentinel objects, and delegation of locate/query/remove/stat to endpoint-specific HTTP filesystem handles.

## Important APIs, Types, and Functions
Local helpers include `urlquote()`, `JoinUrl()`, `StatHandler`, `StatHandlerDirectory`, `DirListResponseHandler`, and `MkdirHandler`. Main methods are `Filesystem::DirList()`, `GetFSHandle()`, `Locate()`, `MkDir()`, `Query()`, `Rm()`, `RmDir()`, `Stat()`, property accessors, and `S3HeaderCallout::GetHeaders()`.

## Control Flow
`DirList()` converts S3 path to HTTPS bucket URL, appends `list-type=2`, delimiter, encoding, and prefix parameters, then downloads the listing with a signing callout. `DirListResponseHandler` parses XML into `XrdCl::DirectoryList`, follows continuation tokens until complete, and can short-circuit for existence checks. `Stat()` first delegates to HTTP stat; on not-found it issues a listing for the same prefix and converts a successful prefix match into directory `StatInfo`. `MkDir()` writes a zero-byte sentinel object and closes it asynchronously via `MkdirHandler`.

## State and Persistence Behavior
Per-instance state includes base `XrdCl::URL`, logger, properties, a shared-mutex-protected map from HTTPS endpoint to `XrdCl::FileSystem*`, and an embedded header callout. Persistent remote effects are S3 object creation/removal, especially sentinel files used to model empty directories.

## Dependencies and Integration Points
Depends on TinyXML, `XrdClS3DownloadHandler`, `XrdClS3Factory`, XrdCl URL/log/filesystem/stat/list classes, and the HTTP header callout property convention. It integrates S3 directory semantics into XRootD's filesystem plugin contract.

## Risks and Edge Cases
`urlquote()` uses `std::to_string(val)` after `%`, which emits decimal rather than two-digit hex percent encoding and may mishandle negative `char` values. XML parsing assumes a non-null root and specific S3 element names. Time parsing uses `mktime()` on UTC-looking `Z` timestamps, which can apply local timezone. Handler self-ownership patterns require every async path to release/delete exactly once. Endpoint handles are raw pointers and are not visibly freed in the destructor.

## Test Signals
Tests should exercise listing XML with files, common prefixes, continuation tokens, empty prefixes, sentinel-only directories, malformed XML, timeout expiry, and not-found stat fallback. Integration tests should verify mkdir/rmdir sentinel behavior and signed filesystem calls against an S3-compatible endpoint.
