# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFilesystem.cc

## Purpose
`XrdClHttpFilesystem.cc` implements the HTTP filesystem plugin, translating XrdCl filesystem-level operations into HTTP/WebDAV curl operations against a base URL.

## Important APIs and Functions
Implemented methods include constructor/destructor, `DirList`, `GetProperty`, `Locate`, `MkDir`, `Query`, `Rm`, `RmDir`, `SetProperty`, `Stat`, `SendResponseInfo`, `GetConnCallout`, and `GetCurrentURL`. Operations enqueue `CurlListdirOp`, `CurlMkcolOp`, `CurlChecksumOp`, `CurlQueryOp`, `CurlDeleteOp`, and `CurlStatOp`.

## Control Flow
The constructor normalizes the base URL path to `/` and clears query params. Filesystem operations build a full URL with `GetCurrentURL`, compute a header timeout through `Factory`, create the appropriate curl operation, and push it to the shared queue. `Locate` is synchronous and returns the base host/port as an online read location. `RmDir` delegates to `Rm`. `Query` handles checksum and XAttr codes and rejects other query codes.

## State and Persistence
The object stores base URL, queue, logger, mutable properties under shared mutex, and an atomic header callout pointer. Remote persistent changes occur through MKCOL and DELETE operations. The `XrdClHttpQueryParam` property can alter future request URLs.

## Dependencies and Integration Points
It integrates XrdCl `FileSystemPlugIn`, URL, logging, location and buffer response types, HTTP operation classes, response-info opt-in, and the connection/header callout property conventions also used by `File`.

## Risks and Test Signals
`GetConnCallout` uses `if (!GetProperty(...) && pointer_str.empty())`, which returns null for missing empty strings but may still try parsing non-empty values when `GetProperty` fails unexpectedly. `GetCurrentURL` uses `':'` instead of `'&'` when appending a query to a URL that already has `?`, which looks suspicious. Tests should cover URL normalization, query param appending, checksum type selection, queue produce exceptions, response-info opt-in, header/callout pointer parsing, and all unsupported query codes.
