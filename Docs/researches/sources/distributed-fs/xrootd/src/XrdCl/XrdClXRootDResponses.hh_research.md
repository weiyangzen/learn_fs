# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDResponses.hh

## Purpose

This header defines the public response/result data model used by the XRootD client layer. It gives higher-level `File`, `FileSystem`, async readers, message handlers, copy jobs, ZIP archive helpers, and EC handlers typed wrappers around raw XRoot protocol replies: locate results, protocol info, stat and VFS stat results, directory listings, open results, read/page-read/vector-read payload descriptions, host redirect lists, extended attribute replies, and callback interfaces.

The file is declaration-heavy; parsing and PIMPL bodies live in `XrdClXRootDResponses.cc`, while this header fixes the object ownership, status shape, iterator API, and callback contract that most of `src/XrdCl` includes.

## Important APIs, types, and functions

- `LocationInfo` stores parsed `kXR_locate` locations. Nested `Location` records carry an address, `LocationType` (`ManagerOnline`, `ManagerPending`, `ServerOnline`, `ServerPending`), and `AccessType` (`Read`, `ReadWrite`). `ParseServerResponse()` and private `ProcessLocation()` populate the vector.
- `XRootDStatus` extends `Status` with a server/error message string, `GetErrorMessage()`, `SetErrorMessage()`, and `ToStr()`. For `errErrorResponse`, `ToStr()` formats the server error number and message.
- `xattr_t`, `XAttrStatus`, and `XAttr` represent extended attribute name/value/status results. `FileStateHandler` and `FileSystem` are friends because they construct and fill these response objects.
- `BinaryDataInfo` is an alias for `Buffer`, used when a response body is opaque bytes.
- `ProtocolInfo` carries XRoot protocol version and host/server flags, exposing `GetVersion()`, `GetHostInfo()`, and `TestHostInfo()`.
- `StatInfo` is the main file metadata object. It uses `std::unique_ptr<StatInfoImpl>` and exposes id, size, flags, modification/change/access times, mode, owner, group, checksum, `ParseServerResponse()`, `ExtendedFormat()`, and `HasChecksum()`.
- `StatInfoVFS` stores `kXR_vfs` values: read/write nodes/free/utilization and staging nodes/free/utilization, filled by `ParseServerResponse()`.
- `DirectoryList` owns a vector of heap-allocated `ListEntry` objects. `ListEntry` owns an optional `StatInfo*`, strips leading slashes from entry names, and exposes host/name/stat accessors. The list parses plain and stat-rich directory responses and has `HasStatInfo()` to classify server payloads.
- `OpenInfo` owns optional `StatInfo*` and stores the four-byte file handle plus 64-bit session id returned from open.
- `ChunkInfo`, `PageInfo`, `RetryInfo`, `TractInfo`, `ChunkList`, `TractList`, and `VectorReadInfo` model read-like results: byte chunks, page-read data plus CRC checksums/repair count, retry page ranges, vector preread tracts, and vector-read aggregate size/chunks.
- `HostInfo` and `HostList` describe redirected hosts, including flags, protocol version, whether the entry came from a load balancer, and its `URL`.
- `ResponseHandler` is the async callback base class. `HandleResponseWithHosts()` defaults to deleting `HostList` and delegating to `HandleResponse()`. Static `Wrap()` factories adapt lambdas taking either references or pointers.

## Control flow

Consumers normally receive raw protocol bodies in `XrdClXRootDMsgHandler.cc`, allocate one of these response objects, invoke a `ParseServerResponse()` method when required, wrap it in `AnyObject`, and pass it to a `ResponseHandler`. File-system convenience APIs then unwrap these types or expose them to the caller.

The response ownership flow is deliberately explicit. Many objects are allocated with `new` and transferred through `AnyObject` or callbacks. `DirectoryList` and `OpenInfo` destructors delete nested entries/stat info; `ResponseHandler::HandleResponseWithHosts()` deletes the host list by default; lambda wrappers in the `.cc` implementation are responsible for deleting or forwarding status/response pointers according to their callback flavor.

`StatInfo`, `PageInfo`, and `RetryInfo` hide internal layout behind PIMPLs, which keeps this public header stable while allowing the implementation file to change parser/storage details. Helper methods such as `TimeToString()` and `OctToString()` centralize presentation of metadata parsed elsewhere.

## State and persistence behavior

All state is in-memory response state. There is no filesystem persistence here. The main persistent-like behavior is ownership/lifetime: `DirectoryList` owns `ListEntry*`; each `ListEntry` owns its `StatInfo*`; `OpenInfo` owns its optional `StatInfo*`; `StatInfo`, `PageInfo`, and `RetryInfo` own their PIMPLs. `LocationInfo` and `VectorReadInfo` use value vectors. `XRootDStatus` stores an additional message string alongside the inherited status fields.

Because these objects cross asynchronous boundaries, their destructors and pointer ownership are integration-critical. A caller that passes a raw `StatInfo*` into `ListEntry`, or a `ListEntry*` into `DirectoryList::Add()`, gives up ownership.

## Dependencies and integration points

The header depends on `XrdClBuffer.hh`, `XrdClStatus.hh`, `XrdClURL.hh`, `XrdClAnyObject.hh`, `XProtocol/XProtocol.hh`, STL containers, tuples, function wrappers, and `sys/uio.h`. It is widely included by client subsystems including `XrdClFile.hh`, `XrdClFileSystem.hh`, `XrdClFileStateHandler`, async reader/writer classes, socket/message queue code, message handlers, ZIP cache/archive code, EC helpers, and copy utilities.

Protocol constants from `XProtocol.hh` define many enum values, especially stat flags and protocol host flags. The concrete parser implementation in `XrdClXRootDResponses.cc` is therefore part of the behavioral contract even though the declarations live here.

## Risks and edge cases

- Raw pointer ownership is easy to misuse. `DirectoryList::ListEntry::SetStatInfo()` overwrites `pStatInfo` without deleting an existing pointer, so callers must avoid replacing owned stat info after construction unless they have handled the old pointer.
- `At()` methods do not bounds-check, so callers must validate sizes.
- `ResponseHandler` default methods do nothing except host-list deletion; missing overrides can silently drop responses.
- `XRootDStatus::ToStr()` special-cases only `errErrorResponse`; other server-message statuses append the message to `Status::ToString()`.
- `TimeToString()` uses `gmtime()` and `strftime()` without explicit null checks; invalid or platform-problematic time values would format poorly.
- The response parsers declared here consume text/binary server formats; malformed responses must be rejected in the `.cc` implementation, not in this header.
- Many response objects are mutable and not intrinsically synchronized. They should be populated before callback handoff or otherwise externally protected.

## Test signals

Useful tests should cover parser success/failure for locate, stat extended/basic formats, VFS stats, directory lists with and without stat blocks, page-read retry/checksum containers, and lambda `ResponseHandler::Wrap()` ownership behavior. Integration signals appear in `XrdClXRootDMsgHandler.cc` paths that call these parsers and in `XrdClFS.cc`/`XrdClFileSystem.cc` code that consumes `StatInfo`, `DirectoryList`, and `LocationInfo`. Memory-safety tests are valuable around destructor ownership and repeated callback paths.
